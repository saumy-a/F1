"""
Analytics router for advanced F1 statistics and metrics.
"""
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.models.analytics import (
    PerformanceTrend,
    ConsistencyScore,
    DNFRate,
    FormIndicator,
    PointsPerRace,
    QualifyingRaceCorrelation,
    TeamReliability,
    ConstructorDevelopment,
    DriverPairing,
    CircuitPerformance,
    CircuitDifficulty,
    DriverComparison,
    SeasonComparison,
    PercentileRankings,
    ChampionshipProjection
)
from app.services.analytics import (
    calculate_performance_trends,
    calculate_consistency_score,
    calculate_dnf_rate,
    calculate_points_per_race,
    calculate_qualifying_race_correlation,
    calculate_form_indicator,
    calculate_team_reliability,
    calculate_constructor_development,
    calculate_driver_pairing,
    calculate_circuit_performance,
    calculate_circuit_difficulty,
    calculate_multi_driver_comparison,
    calculate_season_comparison,
    calculate_percentile_rankings,
    calculate_championship_projection
)
from app.services.jolpica import fetch_driver_race_results, fetch_race_schedule, fetch_driver_standings
from app.cache.redis import redis_cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/analytics/trends/{driver_id}/{year}",
    response_model=PerformanceTrend,
    summary="Get performance trends",
    description="Calculate performance trends for a driver over a season"
)
async def get_performance_trends(
    request: Request,
    driver_id: str,
    year: str
):
    """
    Get performance trend analysis for a driver.
    
    - **driver_id**: Driver identifier (e.g., "max_verstappen", "hamilton")
    - **year**: Season year (e.g., "2024", "2023")
    
    Returns Plotly-compatible chart data showing performance over the season.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating performance trends for driver={driver_id}, year={year}")
        
        # Step 1: Fetch raw data
        race_results = await fetch_driver_race_results(
            driver_id=driver_id,
            year=year,
            request_id=request_id
        )
        
        if not race_results:
            raise HTTPException(status_code=404, detail=f"No race results found for driver {driver_id} in {year}")
        
        # Step 2: Calculate
        result = calculate_performance_trends(race_results=race_results)
        
        if result is None or result.empty:
            raise HTTPException(status_code=404, detail=f"No performance data found for driver {driver_id} in {year}")
        
        # Step 3: Return
        logger.info(f"[{request_id}] Successfully calculated performance trends")
        return PerformanceTrend.model_validate({"data": result.to_dict('records')})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating performance trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while calculating performance trends")


@router.get(
    "/analytics/consistency/{driver_id}/{year}",
    response_model=ConsistencyScore,
    summary="Get consistency score",
    description="Calculate consistency metrics for a driver"
)
async def get_consistency_score(
    request: Request,
    driver_id: str,
    year: str
):
    """
    Get consistency score and metrics for a driver.
    
    - **driver_id**: Driver identifier
    - **year**: Season year
    
    Returns consistency score (0-100), standard deviation, and average position.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating consistency score for driver={driver_id}, year={year}")
        
        # Step 1: Fetch raw data using the Jolpica service
        race_results = await fetch_driver_race_results(
            driver_id=driver_id,
            year=year,
            request_id=request_id
        )
        
        if not race_results:
            logger.warning(f"[{request_id}] No race results found for {driver_id} in {year}")
            raise HTTPException(
                status_code=404,
                detail=f"No race results found for driver {driver_id} in {year}"
            )
        
        # Step 2: Run the pure calculation function
        result = calculate_consistency_score(race_results=race_results)
        
        if result is None:
            logger.warning(f"[{request_id}] Insufficient data for consistency calculation")
            raise HTTPException(
                status_code=422,
                detail="Insufficient data: fewer than 5 completed races"
            )
        
        # Step 3: Return validated Pydantic response
        logger.info(f"[{request_id}] Successfully calculated consistency score: {result.get('consistency_score', 0):.2f}")
        return ConsistencyScore.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating consistency score: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating consistency score"
        )


@router.get(
    "/analytics/form/{driver_id}/{year}",
    response_model=FormIndicator,
    summary="Get form indicator",
    description="Analyze recent form for a driver"
)
async def get_form_indicator(
    request: Request,
    driver_id: str,
    year: str,
    last_n: int = Query(5, ge=1, le=10, description="Number of recent races to analyze")
):
    """Get recent form analysis for a driver."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating form indicator for driver={driver_id}, year={year}, last_n={last_n}")
        
        race_results = await fetch_driver_race_results(driver_id=driver_id, year=year, request_id=request_id)
        if not race_results:
            raise HTTPException(status_code=404, detail=f"No race results found for driver {driver_id} in {year}")
        
        result = calculate_form_indicator(race_results=race_results, n_races=last_n)
        if result is None:
            raise HTTPException(status_code=404, detail=f"No form data found for driver {driver_id} in {year}")
        
        logger.info(f"[{request_id}] Successfully calculated form indicator: {result.get('trend', 'unknown')}")
        return FormIndicator.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating form indicator: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while calculating form indicator")


@router.get(
    "/analytics/dnf/{driver_id}/{year}",
    response_model=DNFRate,
    summary="Get DNF rate",
    description="Calculate DNF statistics for a driver"
)
async def get_dnf_rate(
    request: Request,
    driver_id: str,
    year: str
):
    """Get DNF (Did Not Finish) statistics for a driver."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating DNF rate for driver={driver_id}, year={year}")
        
        race_results = await fetch_driver_race_results(driver_id=driver_id, year=year, request_id=request_id)
        if not race_results:
            raise HTTPException(status_code=404, detail=f"No race results found for driver {driver_id} in {year}")
        
        result = calculate_dnf_rate(race_results=race_results)
        if result is None:
            raise HTTPException(status_code=404, detail=f"No DNF data found for driver {driver_id} in {year}")
        
        logger.info(f"[{request_id}] Successfully calculated DNF rate: {result.get('dnf_rate', 0):.2%}")
        return DNFRate.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating DNF rate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while calculating DNF rate")



@router.get(
    "/analytics/points-per-race/{driver_id}/{year}",
    response_model=PointsPerRace,
    summary="Get points per race average",
    description="Calculate average points per race for a driver"
)
async def get_points_per_race(
    request: Request,
    driver_id: str,
    year: str
):
    """Get points per race average for a driver."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating points per race for driver={driver_id}, year={year}")
        
        race_results = await fetch_driver_race_results(driver_id=driver_id, year=year, request_id=request_id)
        if not race_results:
            raise HTTPException(status_code=404, detail=f"No race results found for driver {driver_id} in {year}")
        
        result = calculate_points_per_race(race_results=race_results)
        if result is None:
            raise HTTPException(status_code=404, detail=f"No points data found for driver {driver_id} in {year}")
        
        logger.info(f"[{request_id}] Successfully calculated points per race: {result.get('points_per_race', 0):.2f}")
        return PointsPerRace.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating points per race: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while calculating points per race")


@router.get(
    "/analytics/qualifying-correlation/{driver_id}/{year}",
    response_model=QualifyingRaceCorrelation,
    summary="Get qualifying-race correlation",
    description="Calculate correlation between qualifying and race performance"
)
async def get_qualifying_race_correlation(
    request: Request,
    driver_id: str,
    year: str
):
    """Get correlation between qualifying and race performance."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating qualifying-race correlation for driver={driver_id}, year={year}")
        
        race_results = await fetch_driver_race_results(driver_id=driver_id, year=year, request_id=request_id)
        if not race_results:
            raise HTTPException(status_code=404, detail=f"No race results found for driver {driver_id} in {year}")
        
        result = calculate_qualifying_race_correlation(race_results=race_results)
        if result is None:
            raise HTTPException(status_code=404, detail=f"No correlation data found for driver {driver_id} in {year}")
        
        logger.info(f"[{request_id}] Successfully calculated correlation: {result.get('correlation', 0):.3f}")
        return QualifyingRaceCorrelation.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating qualifying-race correlation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while calculating correlation")


@router.get(
    "/analytics/team-reliability/{constructor_id}/{year}",
    response_model=TeamReliability,
    summary="Get team reliability",
    description="Calculate reliability metrics for a constructor"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_team_reliability(
    request: Request,
    constructor_id: str,
    year: str
):
    """
    Get reliability metrics for a constructor.
    
    - **constructor_id**: Constructor identifier (e.g., "red_bull", "ferrari")
    - **year**: Season year
    
    Returns total races, DNF count, and reliability rate.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating team reliability for constructor={constructor_id}, year={year}")
        
        result = await calculate_team_reliability(
            constructor_id=constructor_id,
            year=year,
            request_id=request_id
        )
        
        if result is None:
            logger.warning(f"[{request_id}] No reliability data found for {constructor_id} in {year}")
            raise HTTPException(
                status_code=404,
                detail=f"No reliability data found for constructor {constructor_id} in {year}"
            )
        
        logger.info(f"[{request_id}] Successfully calculated team reliability: {result.get('reliability_rate', 0):.2%}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating team reliability: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating team reliability"
        )


@router.get(
    "/analytics/constructor-development/{constructor_id}/{year}",
    response_model=ConstructorDevelopment,
    summary="Get constructor development",
    description="Analyze constructor development trajectory over season"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_constructor_development(
    request: Request,
    constructor_id: str,
    year: str
):
    """
    Get constructor development analysis.
    
    - **constructor_id**: Constructor identifier
    - **year**: Season year
    
    Returns early/late season averages and development trend.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating constructor development for constructor={constructor_id}, year={year}")
        
        result = await calculate_constructor_development(
            constructor_id=constructor_id,
            year=year,
            request_id=request_id
        )
        
        if result is None:
            logger.warning(f"[{request_id}] No development data found for {constructor_id} in {year}")
            raise HTTPException(
                status_code=404,
                detail=f"No development data found for constructor {constructor_id} in {year}"
            )
        
        logger.info(f"[{request_id}] Successfully calculated constructor development: {result.get('trend', 'unknown')}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating constructor development: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating constructor development"
        )


@router.get(
    "/analytics/driver-pairing/{constructor_id}/{year}",
    response_model=DriverPairing,
    summary="Get driver pairing analysis",
    description="Analyze driver pairing within a team"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_driver_pairing(
    request: Request,
    constructor_id: str,
    year: str
):
    """
    Get driver pairing analysis for a constructor.
    
    - **constructor_id**: Constructor identifier
    - **year**: Season year
    
    Returns head-to-head comparison and average positions.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating driver pairing for constructor={constructor_id}, year={year}")
        
        result = await calculate_driver_pairing(
            constructor_id=constructor_id,
            year=year,
            request_id=request_id
        )
        
        if result is None:
            logger.warning(f"[{request_id}] No driver pairing data found for {constructor_id} in {year}")
            raise HTTPException(
                status_code=404,
                detail=f"No driver pairing data found for constructor {constructor_id} in {year}"
            )
        
        logger.info(f"[{request_id}] Successfully calculated driver pairing")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating driver pairing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating driver pairing"
        )



# Comparative and Circuit Analytics Endpoints


class DriverComparisonRequest(BaseModel):
    """Request model for multi-driver comparison."""
    driver_ids: List[str] = Field(min_length=2, max_length=5, description="List of 2-5 driver IDs to compare")
    year: str = Field(description="Season year")


@router.post(
    "/analytics/compare",
    response_model=DriverComparison,
    summary="Compare multiple drivers",
    description="Compare performance metrics across multiple drivers"
)
@redis_cache(ttl=600, namespace="analytics")
async def compare_drivers(
    request: Request,
    comparison_request: DriverComparisonRequest
):
    """
    Compare multiple drivers across various metrics.
    
    Request body:
    - **driver_ids**: List of 2-5 driver identifiers
    - **year**: Season year
    
    Returns comparative metrics and chart data for visualization.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        driver_ids = comparison_request.driver_ids
        year = comparison_request.year
        
        logger.info(f"[{request_id}] Comparing drivers {driver_ids} for year={year}")
        
        # Fetch race results for each driver
        drivers_data = {}
        for driver_id in driver_ids:
            race_results = await fetch_driver_race_results(
                driver_id=driver_id,
                year=year,
                request_id=request_id
            )
            if race_results:
                drivers_data[driver_id] = race_results
                logger.debug(f"[{request_id}] Fetched {len(race_results)} races for {driver_id}")
        
        if len(drivers_data) < 2:
            logger.warning(f"[{request_id}] Insufficient data: only {len(drivers_data)} drivers have race results")
            raise HTTPException(
                status_code=422,
                detail=f"Insufficient data: need at least 2 drivers with race results. Found {len(drivers_data)} of {len(driver_ids)}"
            )
        
        # Calculate comparison
        logger.debug(f"[{request_id}] Calculating comparison for {len(drivers_data)} drivers")
        result_df = calculate_multi_driver_comparison(
            drivers_data=drivers_data,
            metrics=['avg_finish', 'points_per_race', 'consistency_score', 'dnf_rate']
        )
        
        if result_df is None or result_df.empty:
            logger.warning(f"[{request_id}] No comparison data generated for drivers {driver_ids} in {year}")
            raise HTTPException(
                status_code=422,
                detail=f"Could not calculate comparison metrics for the specified drivers"
            )
        
        # Format response to match DriverComparison model
        # Extract driver names and metrics (excluding driver_name column)
        driver_names = result_df['driver_name'].tolist() if 'driver_name' in result_df.columns else list(drivers_data.keys())
        metrics_df = result_df.drop(columns=['driver_name']) if 'driver_name' in result_df.columns else result_df
        
        result = {
            "drivers": driver_names,
            "metrics": metrics_df.to_dict('list')
        }
        
        logger.info(f"[{request_id}] Successfully compared {len(driver_ids)} drivers")
        return DriverComparison.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"[{request_id}] Error comparing drivers: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )

@router.get(
    "/analytics/circuit/{circuit_id}",
    response_model=CircuitPerformance,
    summary="Get circuit performance",
    description="Get performance metrics for a specific circuit"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_circuit_performance(
    request: Request,
    circuit_id: str,
    year: str = Query(..., description="Season year")
):
    """
    Get circuit-specific performance metrics.
    
    - **circuit_id**: Circuit identifier (e.g., "monaco", "monza")
    - **year**: Season year
    
    Returns performance data by driver/team at the circuit.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching circuit performance for circuit={circuit_id}, year={year}")
        
        # Fetch all race results for the year
        race_schedule = await fetch_race_schedule(year=year, request_id=request_id)
        
        if not race_schedule:
            raise HTTPException(status_code=404, detail=f"No races found for {year}")
        
        # Filter races by circuit (case-insensitive substring match)
        filtered_races = [
            r for r in race_schedule 
            if circuit_id.lower() in r.get("raceName", "").lower() or 
               circuit_id.lower() in r.get("Circuit", {}).get("circuitName", "").lower()
        ]
        
        logger.debug(f"[{request_id}] Found {len(filtered_races)} races matching circuit '{circuit_id}'")
        
        if not filtered_races:
            raise HTTPException(
                status_code=404,
                detail=f"No races found for circuit '{circuit_id}' in {year}"
            )
        
        # Calculate circuit performance
        result = calculate_circuit_performance(
            driver_results=filtered_races,
            circuit_name=circuit_id,
            min_appearances=1
        )
        
        if result is None:
            raise HTTPException(status_code=422, detail="Insufficient data for this circuit")
        
        # Format response to match CircuitPerformance model
        response = {
            "circuit_id": circuit_id,
            "performances": [result]  # Wrap single result in list
        }
        
        logger.info(f"[{request_id}] Successfully fetched circuit performance")
        return CircuitPerformance.model_validate(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching circuit performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching circuit performance"
        )


@router.get(
    "/analytics/circuit-difficulty/{circuit_id}",
    response_model=CircuitDifficulty,
    summary="Get circuit difficulty",
    description="Analyze circuit difficulty metrics"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_circuit_difficulty(
    request: Request,
    circuit_id: str,
    year: str = Query(..., description="Season year")
):
    """
    Get circuit difficulty analysis.
    
    - **circuit_id**: Circuit identifier
    - **year**: Season year
    
    Returns DNF rate, overtakes, and difficulty score.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating circuit difficulty for circuit={circuit_id}, year={year}")
        
        result = await calculate_circuit_difficulty(
            circuit_id=circuit_id,
            year=year,
            request_id=request_id
        )
        
        if result is None:
            logger.warning(f"[{request_id}] No circuit difficulty data found for {circuit_id} in {year}")
            raise HTTPException(
                status_code=404,
                detail=f"No circuit difficulty data found for {circuit_id} in {year}"
            )
        
        logger.info(f"[{request_id}] Successfully calculated circuit difficulty")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating circuit difficulty: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating circuit difficulty"
        )


@router.get(
    "/analytics/projection/{year}",
    response_model=ChampionshipProjection,
    summary="Get championship projection",
    description="Project championship outcome based on current standings"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_championship_projection(
    request: Request,
    year: str
):
    """
    Get championship projection for the season.
    
    - **year**: Season year
    
    Returns projected winner, final points, and confidence level.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        from datetime import datetime
        
        logger.info(f"[{request_id}] Calculating championship projection for year={year}")
        
        # Check if this is the current year
        current_year = str(datetime.now().year)
        if year != current_year:
            raise HTTPException(
                status_code=400,
                detail="Championship projection is only available for the current season"
            )
        
        # Fetch current standings
        from app.services.jolpica import fetch_driver_standings
        standings = await fetch_driver_standings(year=year, request_id=request_id)
        
        if not standings:
            raise HTTPException(status_code=404, detail=f"No standings found for {year}")
        
        # Fetch race schedule to calculate remaining races
        race_schedule = await fetch_race_schedule(year=year, request_id=request_id)
        
        if not race_schedule:
            raise HTTPException(status_code=404, detail=f"No race schedule found for {year}")
        
        # Calculate remaining races (races after today)
        today = datetime.now().date()
        remaining_races = sum(
            1 for race in race_schedule 
            if datetime.strptime(race.get('date', '9999-12-31'), '%Y-%m-%d').date() > today
        )
        
        logger.debug(f"[{request_id}] Remaining races: {remaining_races}")
        
        # Calculate projection
        result = calculate_championship_projection(
            current_standings=standings,
            remaining_races=remaining_races,
            year=year
        )
        
        if not result or not result.get('projections'):
            raise HTTPException(status_code=422, detail="Insufficient data for projection")
        
        # Format response to match ChampionshipProjection model
        projections = result.get('projections', [])
        projected_winner = projections[0]['driver_name'] if projections else "Unknown"
        projected_points = {p['driver_name']: p['projected_points'] for p in projections}
        
        response = {
            "projected_winner": projected_winner,
            "projected_points": projected_points,
            "confidence": 0.7,  # Basic confidence score
            "races_remaining": remaining_races
        }
        
        logger.info(f"[{request_id}] Successfully calculated championship projection")
        return ChampionshipProjection.model_validate(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating championship projection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating championship projection"
        )


@router.get(
    "/analytics/season-comparison/{driver_id}",
    response_model=SeasonComparison,
    summary="Compare driver across seasons",
    description="Compare a driver's performance across multiple seasons"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_season_comparison(
    request: Request,
    driver_id: str,
    years: List[str] = Query(..., description="List of season years to compare")
):
    """
    Compare a driver's performance across multiple seasons.
    
    - **driver_id**: Driver identifier
    - **years**: List of season years (e.g., ["2022", "2023", "2024"])
    
    Returns metrics across seasons and chart data.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Comparing seasons for driver={driver_id}, years={years}")
        
        result = await calculate_season_comparison(
            driver_id=driver_id,
            years=years,
            request_id=request_id
        )
        
        if result is None:
            logger.warning(f"[{request_id}] No season comparison data found for {driver_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No season comparison data found for driver {driver_id}"
            )
        
        logger.info(f"[{request_id}] Successfully compared {len(years)} seasons")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error comparing seasons: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while comparing seasons"
        )


@router.get(
    "/analytics/percentile-rankings/{year}",
    response_model=PercentileRankings,
    summary="Get percentile rankings",
    description="Get percentile rankings for all drivers"
)
@redis_cache(ttl=600, namespace="analytics")
async def get_percentile_rankings(
    request: Request,
    year: str
):
    """
    Get percentile rankings for all drivers in a season.
    
    - **year**: Season year
    
    Returns percentile rankings across various metrics.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Calculating percentile rankings for year={year}")
        
        result = await calculate_percentile_rankings(
            year=year,
            request_id=request_id
        )
        
        if result is None:
            logger.warning(f"[{request_id}] No percentile ranking data found for {year}")
            raise HTTPException(
                status_code=404,
                detail=f"No percentile ranking data found for {year}"
            )
        
        logger.info(f"[{request_id}] Successfully calculated percentile rankings")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error calculating percentile rankings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while calculating percentile rankings"
        )
