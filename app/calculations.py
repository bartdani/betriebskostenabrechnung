from sqlalchemy import func, or_
from app import db
from app.models import ConsumptionData, Apartment, CostType, ApartmentShare, OccupancyPeriod
from collections import defaultdict

def calculate_consumption_allocation(cost_type_id, total_cost, period_start, period_end):
    """
    Berechnet die Kostenverteilung für einen bestimmten Kosten-Typ basierend auf Verbrauch.

    Args:
        cost_type_id: Die ID des zu verteilenden CostType.
        total_cost: Der Gesamtbetrag, der verteilt werden soll.
        period_start: Startdatum des Abrechnungszeitraums.
        period_end: Enddatum des Abrechnungszeitraums.

    Returns:
        dict: Ein Dictionary {apartment_id: allocated_cost} oder None bei Fehlern.
    """
    
    # Sicherstellen, dass der CostType existiert und vom Typ 'consumption' ist
    cost_type = db.session.get(CostType, cost_type_id) # Verwendung der neueren Session.get Methode
    if not cost_type or cost_type.type != 'consumption':
        print(f"Error: CostType {cost_type_id} not found or not type 'consumption'.")
        return {}

    # 1. Alle relevanten Verbrauchsdaten im Zeitraum holen
    consumption_query = db.session.query(
        ConsumptionData.apartment_id,
        func.sum(ConsumptionData.value).label('total_value')
    ).filter(
        ConsumptionData.cost_type_id == cost_type_id,
        ConsumptionData.date >= period_start,
        ConsumptionData.date <= period_end
    ).group_by(
        ConsumptionData.apartment_id
    )
    
    all_consumptions = consumption_query.all()

    # 2. Gesamtverbrauch berechnen
    total_consumption = sum(c.total_value for c in all_consumptions if c.total_value is not None)

    allocation = {}
    
    # 3. Anteile berechnen, wenn Gesamtverbrauch > 0
    if total_consumption > 0:
        for consumption in all_consumptions:
            if consumption.total_value is not None and consumption.total_value > 0:
                apartment_id = consumption.apartment_id
                apartment_consumption = consumption.total_value
                allocated_cost = (apartment_consumption / total_consumption) * total_cost
                allocation[apartment_id] = round(allocated_cost, 2) # Runden auf 2 Dezimalstellen
            elif consumption.total_value is not None and consumption.total_value <= 0:
                 # Explizit 0 zuweisen, wenn Verbrauch <= 0 war
                 allocation[consumption.apartment_id] = 0.00
    else:
        print(f"Warning: Total consumption for CostType {cost_type_id} in period is 0 or less. No allocation possible.")
        # Optional: Kosten gleichmäßig verteilen? Vorerst nicht.
        # Fallback: Jedem Apartment, das theoretisch hätte verbrauchen können, 0 zuweisen?
        # Holen aller Apartments, die diesen CostType haben könnten (komplexer)
        # Einfachster Fall: Leeres Dictionary zurückgeben oder 0 für die mit Einträgen
        for consumption in all_consumptions:
             allocation[consumption.apartment_id] = 0.00

    # Sicherstellen, dass alle Apartments, die im Zeitraum hätten sein können, 
    # aber keinen Verbrauch hatten, auch mit 0 auftauchen? - Vorerst nicht, nur die mit Daten.

    return allocation 

def calculate_share_allocation(cost_type_id, total_cost):
    """
    Berechnet die Kostenverteilung für einen bestimmten Kosten-Typ basierend auf Anteilen.

    Args:
        cost_type_id: Die ID des zu verteilenden CostType (muss Typ 'share' sein).
        total_cost: Der Gesamtbetrag, der verteilt werden soll.

    Returns:
        dict: Ein Dictionary {apartment_id: allocated_cost} oder None bei Fehlern.
    """
    
    # Sicherstellen, dass der CostType existiert und vom Typ 'share' ist
    cost_type = db.session.get(CostType, cost_type_id)
    if not cost_type or cost_type.type != 'share':
        print(f"Error: CostType {cost_type_id} not found or not type 'share'.")
        return {}

    # 1. Alle relevanten Anteilswerte für diesen CostType holen
    share_query = db.session.query(ApartmentShare).filter(
        ApartmentShare.cost_type_id == cost_type_id
    )
    all_shares = share_query.all()

    # 2. Gesamtsumme der Anteile berechnen
    total_share_value = sum(s.value for s in all_shares if s.value is not None)

    allocation = {}

    # 3. Anteile berechnen, wenn Gesamtsumme > 0
    if total_share_value > 0:
        for share in all_shares:
            if share.value is not None and share.value > 0:
                apartment_id = share.apartment_id
                apartment_share_value = share.value
                allocated_cost = (apartment_share_value / total_share_value) * total_cost
                allocation[apartment_id] = round(allocated_cost, 2)
            elif share.value is not None and share.value <= 0:
                 # Explizit 0 zuweisen, wenn Anteil <= 0 ist
                 allocation[share.apartment_id] = 0.00
    else:
        print(f"Warning: Total share value for CostType {cost_type_id} is 0 or less. No allocation possible.")
        # Fallback: Jedem Apartment mit Anteil 0 zuweisen
        for share in all_shares:
            allocation[share.apartment_id] = 0.00
            
    # Anders als beim Verbrauch sollten hier alle Apartments mit einem Share-Eintrag 
    # auch im Ergebnis auftauchen (ggf. mit 0.00).
    
    return allocation 

def calculate_combined_allocation(rules):
    """
    Berechnet die Kostenverteilung basierend auf einer Liste von Regeln,
    die Verbrauchs- und/oder Anteilsschlüssel mit Prozentsätzen kombinieren.

    Args:
        rules (list): Eine Liste von Dictionaries, wobei jedes Dict eine Regel darstellt.
                      Erwartetes Format pro Regel:
                      {'cost_type_id': int, 
                       'percentage': float (0-100),
                       'total_cost_part': float, # Der auf diesen Teil entfallende Kostenbetrag
                       'period_start': date,    # Nur relevant für 'consumption'
                       'period_end': date       # Nur relevant für 'consumption'
                      }

    Returns:
        dict: Ein Dictionary {apartment_id: total_allocated_cost} oder None bei Fehlern.
    """
    final_allocation = defaultdict(float) # Startet jeden neuen Key mit 0.0
    total_percentage = 0
    all_apartments_involved = set() # Um alle potenziell betroffenen Apartments zu sammeln

    if not isinstance(rules, list) or not rules:
        print("Error: Invalid or empty rules list provided.")
        return {}

    for rule in rules:
        try:
            cost_type_id = rule['cost_type_id']
            percentage = rule['percentage']
            total_cost_part = rule['total_cost_part']
            # Periode nur holen, wenn benötigt
            period_start = rule.get('period_start') 
            period_end = rule.get('period_end')
            
            total_percentage += percentage

            cost_type = db.session.get(CostType, cost_type_id)
            if not cost_type:
                print(f"Error: CostType {cost_type_id} in rule not found. Skipping rule.")
                continue # Nächste Regel versuchen oder ganz abbrechen? Vorerst: überspringen

            partial_allocation = None
            if cost_type.type == 'consumption':
                if not period_start or not period_end:
                     print(f"Error: period_start and period_end required for consumption rule (CostType {cost_type_id}). Skipping rule.")
                     continue
                partial_allocation = calculate_consumption_allocation(
                    cost_type_id, total_cost_part, period_start, period_end
                )
            elif cost_type.type == 'share':
                partial_allocation = calculate_share_allocation(
                    cost_type_id, total_cost_part
                )
            else:
                print(f"Error: Unknown CostType type '{cost_type.type}' for CostType {cost_type_id}. Skipping rule.")
                continue
            
            if partial_allocation is None:
                print(f"Warning: Sub-allocation failed for rule with CostType {cost_type_id}. Skipping contribution.")
                # Hier könnte man entscheiden, ob der gesamte Prozess fehlschlagen soll
                continue

            # Ergebnisse zusammenführen
            for apt_id, cost in partial_allocation.items():
                final_allocation[apt_id] += cost
                all_apartments_involved.add(apt_id)
        except KeyError as e:
            print(f"Error: Missing key {e} in rule definition. Skipping rule.")
            continue
        except Exception as e:
            print(f"Error processing rule {rule}: {e}. Skipping rule.")
            continue
        
    # Validierung der Prozentsumme (optional, aber sinnvoll)
    if not (99.99 <= total_percentage <= 100.01): # Toleranz für Rundungsfehler
        print(f"Warning: Sum of percentages ({total_percentage}%) in rules is not 100%.")
        # Hier entscheiden, ob Abbruch oder nur Warnung?

    # Runden der Endergebnisse
    for apt_id in final_allocation:
        final_allocation[apt_id] = round(final_allocation[apt_id], 2)
        
    # Sicherstellen, dass alle Apartments, die in *irgendeiner* Teilberechnung 
    # beteiligt waren, auch im Endergebnis sind (ggf. mit 0.0)
    # Dies ist durch defaultdict bereits sichergestellt.

    return dict(final_allocation) 

def _get_relevant_occupancy_periods(apartment_id, period_start, period_end):
    """Holt alle Belegungsperioden für eine Wohnung, die den Abrechnungszeitraum überschneiden.

    Args:
        apartment_id (int): ID der Wohnung.
        period_start (date): Startdatum des Abrechnungszeitraums.
        period_end (date): Enddatum des Abrechnungszeitraums.

    Returns:
        list: Eine Liste von OccupancyPeriod-Objekten.
    """
    periods = db.session.query(OccupancyPeriod).filter(
        OccupancyPeriod.apartment_id == apartment_id,
        OccupancyPeriod.start_date <= period_end, # Periode beginnt vor oder am Ende des Abrechnungszeitraums
        or_(
            OccupancyPeriod.end_date == None,      # Periode läuft noch oder...
            OccupancyPeriod.end_date >= period_start # Periode endet nach oder am Beginn des Abrechnungszeitraums
        )
    ).order_by(OccupancyPeriod.start_date).all()

    return periods

def calculate_person_days(apartment_id, period_start, period_end):
    """Berechnet die gesamten Personentage für eine Wohnung im Abrechnungszeitraum.

    Args:
        apartment_id (int): ID der Wohnung.
        period_start (date): Startdatum des Abrechnungszeitraums.
        period_end (date): Enddatum des Abrechnungszeitraums.

    Returns:
        int: Gesamte Anzahl der Personentage.
    """
    relevant_periods = _get_relevant_occupancy_periods(apartment_id, period_start, period_end)
    total_person_days = 0

    for period in relevant_periods:
        # Bestimme den tatsächlichen Start- und Endzeitpunkt des Überlappungsintervalls
        overlap_start = max(period.start_date, period_start)
        overlap_end = min(period.end_date, period_end) if period.end_date else period_end

        # Berechne die Anzahl der Tage im Überlappungsintervall (inklusive Start- und Endtag)
        if overlap_end >= overlap_start:
            # +1, da beide Tage inklusive sind
            days_in_overlap = (overlap_end - overlap_start).days + 1 
            person_days = days_in_overlap * period.number_of_occupants
            total_person_days += person_days

    return total_person_days

def calculate_person_day_allocation(cost_type_id, total_cost, period_start, period_end):
    """Berechnet die Kostenverteilung basierend auf Personentagen (pro-rata).

    Args:
        cost_type_id: Die ID des zu verteilenden CostType (ignoriert, da Verteilung 
                      nur auf Personentagen basiert, aber zur Konsistenz).
        total_cost: Der Gesamtbetrag, der verteilt werden soll.
        period_start: Startdatum des Abrechnungszeitraums.
        period_end: Enddatum des Abrechnungszeitraums.

    Returns:
        dict: Ein Dictionary {apartment_id: allocated_cost}.
    """
    
    # 1. Alle Wohnungen holen (wir brauchen die Personentage für alle)
    all_apartments = Apartment.query.all()
    if not all_apartments:
        print("Warning: No apartments found. Cannot calculate person-day allocation.")
        return {}

    # 2. Personentage für jede Wohnung berechnen
    apartment_person_days = {}
    total_system_person_days = 0
    for apt in all_apartments:
        days = calculate_person_days(apt.id, period_start, period_end)
        apartment_person_days[apt.id] = days
        total_system_person_days += days

    allocation = {}

    # 3. Kosten verteilen, wenn Gesamtsumme > 0
    if total_system_person_days > 0:
        for apt_id, person_days in apartment_person_days.items():
            if person_days > 0:
                allocated_cost = (person_days / total_system_person_days) * total_cost
                allocation[apt_id] = round(allocated_cost, 2)
            else:
                allocation[apt_id] = 0.00 # Wohnung hatte keine Personentage im Zeitraum
    else:
        print(f"Warning: Total person-days in period ({period_start} to {period_end}) is 0. No allocation possible.")
        # Allen Wohnungen 0 zuweisen
        for apt_id in apartment_person_days:
            allocation[apt_id] = 0.00

    return allocation 