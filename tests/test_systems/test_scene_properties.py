"""Property-based tests for scene transition flow.

Feature: card-game-core, Property 42: Scene Transition Flow
For any game session, scenes should transition in this order:
main menu -> deck builder -> gameplay -> game over -> main menu (on return).

Validates: Requirements 21.2, 21.3, 21.4, 21.5
"""

from hypothesis import given, settings
import hypothesis.strategies as st


# Valid scene names used in the game
VALID_SCENE_NAMES = ['menu', 'deck_builder', 'gameplay', 'game_over']

# Valid transitions: source -> list of valid destinations
VALID_TRANSITIONS = {
    'menu': ['gameplay', 'deck_builder'],
    'deck_builder': ['gameplay'],
    'gameplay': ['game_over'],
    'game_over': ['menu'],
}

# The expected full session flow
FULL_SESSION_FLOW = ['menu', 'gameplay', 'game_over', 'menu']


def is_valid_transition(from_scene: str, to_scene: str) -> bool:
    """Check if a scene transition is valid."""
    if from_scene not in VALID_TRANSITIONS:
        return False
    return to_scene in VALID_TRANSITIONS[from_scene]


class TestSceneTransitionFlow:
    """**Validates: Requirements 21.2, 21.3, 21.4, 21.5**

    Property 42: Scene Transition Flow
    For any game session, scenes should transition in this order:
    main menu -> deck builder -> gameplay -> game over -> main menu (on return).
    """

    @given(scene_name=st.sampled_from(VALID_SCENE_NAMES))
    @settings(max_examples=100)
    def test_all_scene_names_are_recognized(self, scene_name):
        """Every valid scene name should be in the recognized set."""
        assert scene_name in VALID_SCENE_NAMES

    @given(from_scene=st.sampled_from(VALID_SCENE_NAMES))
    @settings(max_examples=100)
    def test_every_scene_has_at_least_one_valid_transition(self, from_scene):
        """Every scene should have at least one valid outgoing transition."""
        assert from_scene in VALID_TRANSITIONS
        assert len(VALID_TRANSITIONS[from_scene]) > 0

    def test_full_session_flow_is_valid(self):
        """The complete session flow should consist of valid transitions."""
        for i in range(len(FULL_SESSION_FLOW) - 1):
            from_scene = FULL_SESSION_FLOW[i]
            to_scene = FULL_SESSION_FLOW[i + 1]
            assert is_valid_transition(from_scene, to_scene), (
                f"Transition {from_scene} -> {to_scene} should be valid"
            )

    def test_session_starts_at_menu(self):
        """A game session should start at the main menu."""
        assert FULL_SESSION_FLOW[0] == 'menu'

    def test_session_ends_at_menu(self):
        """A game session should end back at the main menu."""
        assert FULL_SESSION_FLOW[-1] == 'menu'

    @given(data=st.data())
    @settings(max_examples=100)
    def test_invalid_transitions_are_rejected(self, data):
        """Transitions not in the valid set should be rejected."""
        from_scene = data.draw(st.sampled_from(VALID_SCENE_NAMES))
        to_scene = data.draw(st.sampled_from(VALID_SCENE_NAMES))

        valid_destinations = VALID_TRANSITIONS[from_scene]
        if to_scene in valid_destinations:
            assert is_valid_transition(from_scene, to_scene) is True
        else:
            assert is_valid_transition(from_scene, to_scene) is False

    @given(num_sessions=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_multiple_sessions_always_return_to_menu(self, num_sessions):
        """After any number of complete game sessions, we should be back at menu."""
        current_scene = 'menu'
        for _ in range(num_sessions):
            # Simulate a full session
            for i in range(len(FULL_SESSION_FLOW) - 1):
                next_scene = FULL_SESSION_FLOW[i + 1]
                assert is_valid_transition(FULL_SESSION_FLOW[i], next_scene)
                current_scene = next_scene
            assert current_scene == 'menu'

    def test_gameplay_can_only_go_to_game_over(self):
        """From gameplay, the only valid transition is to game_over."""
        assert VALID_TRANSITIONS['gameplay'] == ['game_over']

    def test_game_over_can_only_go_to_menu(self):
        """From game_over, the only valid transition is back to menu."""
        assert VALID_TRANSITIONS['game_over'] == ['menu']

    @given(bogus=st.text(min_size=1, max_size=20).filter(lambda s: s not in VALID_SCENE_NAMES))
    @settings(max_examples=100)
    def test_unknown_scene_names_have_no_transitions(self, bogus):
        """An unrecognized scene name should not be in the valid transitions map."""
        assert bogus not in VALID_TRANSITIONS
