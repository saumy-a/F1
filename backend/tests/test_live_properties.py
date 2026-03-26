"""
Property-based tests for live race timing using Hypothesis.

These tests validate universal correctness properties that should hold
for all valid inputs, ensuring the live race timing logic behaves correctly
across a wide range of scenarios.
"""
import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from datetime import datetime, timedelta, timezone
from app.services.live import determine_session_mode


# Property 1: Session Mode Determinism
# =====================================
# **Validates: Requirements 1.2**
# Property: Calling determine_session_mode multiple times with same session data returns same mode

@given(
    hours_before_start=st.integers(min_value=-48, max_value=48),
    session_duration_hours=st.integers(min_value=1, max_value=6)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_session_mode_determinism(hours_before_start, session_duration_hours):
    """
    Property: Session mode determination must be deterministic.
    
    For any given session start/end times, calling determine_session_mode
    multiple times with the same session data should always return the
    same mode value.
    
    This property ensures that:
    - Mode determination is consistent across multiple calls
    - No randomness or time-dependent behavior (except for current time)
    - Same input always produces same output
    """
    # Generate session times relative to a fixed reference point
    reference_time = datetime(2024, 3, 10, 14, 0, 0, tzinfo=timezone.utc)
    date_start = reference_time + timedelta(hours=hours_before_start)
    date_end = date_start + timedelta(hours=session_duration_hours)
    
    # Create session info dict
    session_info = {
        "date_start": date_start.isoformat().replace('+00:00', 'Z'),
        "date_end": date_end.isoformat().replace('+00:00', 'Z')
    }
    
    # Call determine_session_mode multiple times
    mode1 = determine_session_mode(session_info)
    mode2 = determine_session_mode(session_info)
    mode3 = determine_session_mode(session_info)
    
    # Assert determinism: all calls should return the same mode
    assert mode1 == mode2 == mode3, \
        f"Mode determination not deterministic: got {mode1}, {mode2}, {mode3} for session {session_info}"
    
    # Assert mode is one of the valid values
    assert mode1 in ["live", "upcoming", "replay"], \
        f"Invalid mode returned: {mode1}"


@given(
    hours_offset=st.integers(min_value=-100, max_value=100),
    duration_hours=st.integers(min_value=2, max_value=10)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_session_mode_correctness(hours_offset, duration_hours):
    """
    Property: Session mode must correctly reflect session timing.
    
    - If current time < start time: mode should be "upcoming"
    - If start time <= current time <= end time: mode should be "live"
    - If current time > end time: mode should be "replay"
    """
    now = datetime.now(timezone.utc)
    date_start = now + timedelta(hours=hours_offset)
    date_end = date_start + timedelta(hours=duration_hours)
    
    session_info = {
        "date_start": date_start.isoformat().replace('+00:00', 'Z'),
        "date_end": date_end.isoformat().replace('+00:00', 'Z')
    }
    
    mode = determine_session_mode(session_info)
    
    # Re-capture current time to account for execution time
    now_check = datetime.now(timezone.utc)
    
    # Verify mode matches expected value based on timing
    # Use the re-captured time for more accurate comparison
    if now_check < date_start:
        assert mode == "upcoming", \
            f"Expected 'upcoming' for future session, got '{mode}'"
    elif now_check > date_end:
        assert mode == "replay", \
            f"Expected 'replay' for past session, got '{mode}'"
    else:
        assert mode == "live", \
            f"Expected 'live' for current session, got '{mode}'"


@given(
    duration_hours=st.integers(min_value=1, max_value=6)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_session_mode_boundary_conditions(duration_hours):
    """
    Property: Session mode boundaries are handled correctly.
    
    Test edge cases:
    - Session starting in the past but ending in the future (should be "live")
    - Session that started and ended in the past (should be "replay")
    - Session that will start in the future (should be "upcoming")
    """
    now = datetime.now(timezone.utc)
    
    # Test 1: Session currently in progress (started 1 hour ago, ends in future)
    session_in_progress = {
        "date_start": (now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
        "date_end": (now + timedelta(hours=duration_hours)).isoformat().replace('+00:00', 'Z')
    }
    mode_in_progress = determine_session_mode(session_in_progress)
    assert mode_in_progress == "live", \
        f"Session in progress should be 'live', got '{mode_in_progress}'"
    
    # Test 2: Session that ended in the past
    session_ended = {
        "date_start": (now - timedelta(hours=duration_hours + 1)).isoformat().replace('+00:00', 'Z'),
        "date_end": (now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
    }
    mode_ended = determine_session_mode(session_ended)
    assert mode_ended == "replay", \
        f"Session that ended should be 'replay', got '{mode_ended}'"
    
    # Test 3: Session that will start in the future
    session_future = {
        "date_start": (now + timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
        "date_end": (now + timedelta(hours=duration_hours + 1)).isoformat().replace('+00:00', 'Z')
    }
    mode_future = determine_session_mode(session_future)
    assert mode_future == "upcoming", \
        f"Session in future should be 'upcoming', got '{mode_future}'"


@given(
    duration_hours=st.integers(min_value=1, max_value=6)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_session_mode_missing_end_date(duration_hours):
    """
    Property: Session mode handles missing end date gracefully.
    
    When date_end is missing, the function should assume a default
    duration (2 hours) and still return a valid mode.
    """
    now = datetime.now(timezone.utc)
    date_start = now + timedelta(hours=duration_hours)
    
    session_info = {
        "date_start": date_start.isoformat().replace('+00:00', 'Z'),
        "date_end": None
    }
    
    mode = determine_session_mode(session_info)
    
    # Should return a valid mode
    assert mode in ["live", "upcoming", "replay"], \
        f"Invalid mode for session with missing end date: {mode}"


def test_session_mode_missing_start_date():
    """
    Property: Session mode handles missing start date gracefully.
    
    When date_start is missing, the function should default to "replay"
    mode as a safe fallback.
    """
    session_info = {
        "date_end": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    
    mode = determine_session_mode(session_info)
    
    # Should default to "replay" when start date is missing
    assert mode == "replay", \
        f"Expected 'replay' for session with missing start date, got '{mode}'"


@given(
    hours_offset=st.integers(min_value=-48, max_value=48),
    duration_hours=st.integers(min_value=1, max_value=6)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_session_mode_idempotence(hours_offset, duration_hours):
    """
    Property: Session mode determination is idempotent.
    
    Calling the function multiple times in quick succession should
    return the same result (within the same second).
    """
    now = datetime.now(timezone.utc)
    date_start = now + timedelta(hours=hours_offset)
    date_end = date_start + timedelta(hours=duration_hours)
    
    session_info = {
        "date_start": date_start.isoformat().replace('+00:00', 'Z'),
        "date_end": date_end.isoformat().replace('+00:00', 'Z')
    }
    
    # Call function 10 times in quick succession
    modes = [determine_session_mode(session_info) for _ in range(10)]
    
    # All results should be identical
    assert len(set(modes)) == 1, \
        f"Mode determination not idempotent: got different results {set(modes)}"
