"""
Unit tests for analytics API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


# Test Data
MOCK_CONSISTENCY_SCORE = {
    "score": 85.5,
    "std_dev": 2.3,
    "mean_position": 3.5,
    "races_completed": 20
}

MOCK_DNF_RATE = {
    "dnf_count": 2,
    "total_races": 20,
    "dnf_rate": 0.1,
    "dnf_percentage": 10.0
}

MOCK_FORM_INDICATOR = {
    "recent_positions": [2, 1, 3, 2, 1],
    "trend": "improving",
    "average_position": 1.8,
    "races_analyzed": 5
}

MOCK_PERFORMANCE_TREND = {
    "data": [{"x": [1, 2, 3], "y": [5, 3, 2], "type": "scatter"}],
    "layout": {"title": "Performance Trend"}
}

MOCK_POINTS_PER_RACE = {
    "driver_id": "max_verstappen",
    "total_points": 400.0,
    "races_completed": 20,
    "points_per_race": 20.0
}

MOCK_QUALIFYING_CORRELATION = {
    "driver_id": "max_verstappen",
    "correlation_coefficient": 0.85,
    "qualifying_avg": 2.5,
    "race_avg": 2.8,
    "data_points": 20
}

MOCK_TEAM_RELIABILITY = {
    "constructor_id": "red_bull",
    "total_races": 40,
    "dnf_count": 3,
    "reliability_rate": 0.925,
    "reliability_percentage": 92.5
}

MOCK_CONSTRUCTOR_DEVELOPMENT = {
    "constructor_id": "mclaren",
    "early_season_avg": 8.5,
    "late_season_avg": 3.2,
    "improvement": -5.3,
    "trend": "improving"
}

MOCK_DRIVER_PAIRING = {
    "constructor_id": "red_bull",
    "driver1_id": "max_verstappen",
    "driver2_id": "perez",
    "driver1_avg_position": 2.1,
    "driver2_avg_position": 4.5,
    "head_to_head": {"verstappen": 18, "perez": 2}
}

MOCK_DRIVER_COMPARISON = {
    "drivers": ["max_verstappen", "hamilton"],
    "metrics": {
        "avg_position": [2.1, 3.5],
        "points_per_race": [20.0, 15.5]
    },
    "chart_data": {"type": "radar"}
}

MOCK_CIRCUIT_PERFORMANCE = {
    "circuit_id": "monaco",
    "circuit_name": "Monaco",
    "performances": [{"driver": "verstappen", "avg_position": 1.5}],
    "average_winner_time": "1:42:30"
}

MOCK_CIRCUIT_DIFFICULTY = {
    "circuit_id": "monaco",
    "circuit_name": "Monaco",
    "dnf_rate": 0.25,
    "overtakes_avg": 5.2,
    "difficulty_score": 85.0
}

MOCK_CHAMPIONSHIP_PROJECTION = {
    "projected_winner": "max_verstappen",
    "projected_points": {"max_verstappen": 450.0, "hamilton": 380.0},
    "confidence": 0.85,
    "races_remaining": 4
}

MOCK_SEASON_COMPARISON = {
    "driver_id": "hamilton",
    "seasons": ["2022", "2023"],
    "metrics": {"avg_position": [5.5, 4.2]},
    "chart_data": {"type": "bar"}
}

MOCK_PERCENTILE_RANKINGS = {
    "year": "2024",
    "rankings": {
        "max_verstappen": {"points": 95.0, "consistency": 90.0},
        "hamilton": {"points": 75.0, "consistency": 85.0}
    },
    "drivers": ["max_verstappen", "hamilton"]
}


class TestAnalyticsEndpoints:
    """Test suite for analytics endpoints."""
    
    @patch('app.services.analytics.calculate_consistency_score', new_callable=AsyncMock)
    def test_get_consistency_score_success(self, mock_calc):
        """Test successful consistency score retrieval."""
        mock_calc.return_value = MOCK_CONSISTENCY_SCORE
        
        response = client.get("/api/analytics/consistency/max_verstappen/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 85.5
        assert data["races_completed"] == 20
        assert 0 <= data["score"] <= 100
    
    @patch('app.services.analytics.calculate_consistency_score', new_callable=AsyncMock)
    def test_get_consistency_score_not_found(self, mock_calc):
        """Test consistency score with no data."""
        mock_calc.return_value = None
        
        response = client.get("/api/analytics/consistency/unknown_driver/2024")
        
        assert response.status_code == 404
        assert "No consistency data found" in response.json()["detail"]
    
    @patch('app.services.analytics.calculate_dnf_rate', new_callable=AsyncMock)
    def test_get_dnf_rate_success(self, mock_calc):
        """Test successful DNF rate retrieval."""
        mock_calc.return_value = MOCK_DNF_RATE
        
        response = client.get("/api/analytics/dnf/max_verstappen/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["dnf_count"] == 2
        assert data["dnf_rate"] == 0.1
        assert 0 <= data["dnf_rate"] <= 1
    
    @patch('app.services.analytics.calculate_form_indicator', new_callable=AsyncMock)
    def test_get_form_indicator_success(self, mock_calc):
        """Test successful form indicator retrieval."""
        mock_calc.return_value = MOCK_FORM_INDICATOR
        
        response = client.get("/api/analytics/form/max_verstappen/2024?last_n=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["trend"] in ["improving", "declining", "stable"]
        assert len(data["recent_positions"]) == 5
    
    @patch('app.services.analytics.calculate_performance_trends', new_callable=AsyncMock)
    def test_get_performance_trends_success(self, mock_calc):
        """Test successful performance trends retrieval."""
        mock_calc.return_value = MOCK_PERFORMANCE_TREND
        
        response = client.get("/api/analytics/trends/max_verstappen/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "layout" in data
    
    @patch('app.services.analytics.calculate_points_per_race', new_callable=AsyncMock)
    def test_get_points_per_race_success(self, mock_calc):
        """Test successful points per race retrieval."""
        mock_calc.return_value = MOCK_POINTS_PER_RACE
        
        response = client.get("/api/analytics/points-per-race/max_verstappen/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["points_per_race"] >= 0
        assert data["races_completed"] > 0
    
    @patch('app.services.analytics.calculate_qualifying_race_correlation', new_callable=AsyncMock)
    def test_get_qualifying_correlation_success(self, mock_calc):
        """Test successful qualifying-race correlation retrieval."""
        mock_calc.return_value = MOCK_QUALIFYING_CORRELATION
        
        response = client.get("/api/analytics/qualifying-correlation/max_verstappen/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert -1 <= data["correlation_coefficient"] <= 1
    
    @patch('app.services.analytics.calculate_team_reliability', new_callable=AsyncMock)
    def test_get_team_reliability_success(self, mock_calc):
        """Test successful team reliability retrieval."""
        mock_calc.return_value = MOCK_TEAM_RELIABILITY
        
        response = client.get("/api/analytics/team-reliability/red_bull/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["reliability_rate"] <= 1
        assert data["total_races"] >= data["dnf_count"]
    
    @patch('app.services.analytics.calculate_constructor_development', new_callable=AsyncMock)
    def test_get_constructor_development_success(self, mock_calc):
        """Test successful constructor development retrieval."""
        mock_calc.return_value = MOCK_CONSTRUCTOR_DEVELOPMENT
        
        response = client.get("/api/analytics/constructor-development/mclaren/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["trend"] in ["improving", "declining", "stable"]
    
    @patch('app.services.analytics.calculate_driver_pairing', new_callable=AsyncMock)
    def test_get_driver_pairing_success(self, mock_calc):
        """Test successful driver pairing retrieval."""
        mock_calc.return_value = MOCK_DRIVER_PAIRING
        
        response = client.get("/api/analytics/driver-pairing/red_bull/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert "driver1_id" in data
        assert "driver2_id" in data
        assert "head_to_head" in data
    
    @patch('app.services.analytics.calculate_multi_driver_comparison', new_callable=AsyncMock)
    def test_compare_drivers_success(self, mock_calc):
        """Test successful multi-driver comparison."""
        mock_calc.return_value = MOCK_DRIVER_COMPARISON
        
        response = client.post(
            "/api/analytics/compare",
            json={
                "driver_ids": ["max_verstappen", "hamilton"],
                "year": "2024"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["drivers"]) >= 2
        assert "metrics" in data
    
    def test_compare_drivers_invalid_request(self):
        """Test driver comparison with invalid request."""
        # Too few drivers
        response = client.post(
            "/api/analytics/compare",
            json={
                "driver_ids": ["max_verstappen"],
                "year": "2024"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.analytics.calculate_circuit_performance', new_callable=AsyncMock)
    def test_get_circuit_performance_success(self, mock_calc):
        """Test successful circuit performance retrieval."""
        mock_calc.return_value = MOCK_CIRCUIT_PERFORMANCE
        
        response = client.get("/api/analytics/circuit/monaco?year=2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["circuit_id"] == "monaco"
        assert "performances" in data
    
    @patch('app.services.analytics.calculate_circuit_difficulty', new_callable=AsyncMock)
    def test_get_circuit_difficulty_success(self, mock_calc):
        """Test successful circuit difficulty retrieval."""
        mock_calc.return_value = MOCK_CIRCUIT_DIFFICULTY
        
        response = client.get("/api/analytics/circuit-difficulty/monaco?year=2024")
        
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["dnf_rate"] <= 1
        assert 0 <= data["difficulty_score"] <= 100
    
    @patch('app.services.analytics.calculate_championship_projection', new_callable=AsyncMock)
    def test_get_championship_projection_success(self, mock_calc):
        """Test successful championship projection retrieval."""
        mock_calc.return_value = MOCK_CHAMPIONSHIP_PROJECTION
        
        response = client.get("/api/analytics/projection/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert "projected_winner" in data
        assert 0 <= data["confidence"] <= 1
    
    @patch('app.services.analytics.calculate_season_comparison', new_callable=AsyncMock)
    def test_get_season_comparison_success(self, mock_calc):
        """Test successful season comparison retrieval."""
        mock_calc.return_value = MOCK_SEASON_COMPARISON
        
        response = client.get(
            "/api/analytics/season-comparison/hamilton?years=2022&years=2023"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) >= 2
        assert "metrics" in data
    
    @patch('app.services.analytics.calculate_percentile_rankings', new_callable=AsyncMock)
    def test_get_percentile_rankings_success(self, mock_calc):
        """Test successful percentile rankings retrieval."""
        mock_calc.return_value = MOCK_PERCENTILE_RANKINGS
        
        response = client.get("/api/analytics/percentile-rankings/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == "2024"
        assert "rankings" in data
        assert "drivers" in data


class TestAnalyticsEdgeCases:
    """Test edge cases and error handling."""
    
    @patch('app.services.analytics.calculate_consistency_score', new_callable=AsyncMock)
    def test_consistency_score_single_race(self, mock_calc):
        """Test consistency score with only one race."""
        mock_calc.return_value = {
            "score": 100.0,
            "std_dev": 0.0,
            "mean_position": 1.0,
            "races_completed": 1
        }
        
        response = client.get("/api/analytics/consistency/driver/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 100.0  # Perfect consistency with 1 race
    
    @patch('app.services.analytics.calculate_dnf_rate', new_callable=AsyncMock)
    def test_dnf_rate_all_dnfs(self, mock_calc):
        """Test DNF rate when all races are DNFs."""
        mock_calc.return_value = {
            "dnf_count": 5,
            "total_races": 5,
            "dnf_rate": 1.0,
            "dnf_percentage": 100.0
        }
        
        response = client.get("/api/analytics/dnf/driver/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["dnf_rate"] == 1.0
    
    @patch('app.services.analytics.calculate_dnf_rate', new_callable=AsyncMock)
    def test_dnf_rate_no_dnfs(self, mock_calc):
        """Test DNF rate with no DNFs."""
        mock_calc.return_value = {
            "dnf_count": 0,
            "total_races": 20,
            "dnf_rate": 0.0,
            "dnf_percentage": 0.0
        }
        
        response = client.get("/api/analytics/dnf/driver/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data["dnf_rate"] == 0.0
