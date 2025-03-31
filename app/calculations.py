from sqlalchemy import func
from app import db
from app.models import ConsumptionData, Apartment, CostType, ApartmentShare

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
        return None

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
        return None

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