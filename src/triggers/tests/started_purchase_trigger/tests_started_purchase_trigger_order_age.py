import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.mark.parametrize(('time', 'should_be_sent'), [
    ('2032-11-01 15:30', False),  # earlier
    ('2032-12-01 16:00', False),  # too early
    ('2032-12-02 16:00', True),  # ok
    ('2032-12-03 16:00', False),  # too late
])
def test(freezer, trigger, time, should_be_sent):
    freezer.move_to(time)

    assert trigger.should_be_sent() is should_be_sent
