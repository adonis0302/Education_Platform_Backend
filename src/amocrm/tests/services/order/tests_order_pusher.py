import pytest

from _decimal import Decimal

from amocrm.services.orders.order_pusher import AmoCRMOrderPusher
from amocrm.services.orders.order_pusher import AmoCRMOrderPusherException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_push_existing_order_to_amocrm(mocker):
    return mocker.patch("amocrm.tasks.push_existing_order_to_amocrm.apply_async")


@pytest.fixture
def mock_create_amocrm_lead(mocker):
    return mocker.patch("amocrm.tasks.create_amocrm_lead.apply_async")


@pytest.fixture
def mock_update_amocrm_lead(mocker):
    return mocker.patch("amocrm.tasks.update_amocrm_lead.apply_async")


@pytest.fixture
def mock_push_lead(mocker):
    return mocker.patch("amocrm.services.orders.order_pusher.AmoCRMOrderPusher.push_lead")


@pytest.fixture
def mock_push_order(mocker):
    return mocker.patch("amocrm.services.orders.order_pusher.AmoCRMOrderPusher.push_order")


@pytest.fixture
def amocrm_lead(factory):
    return factory.amocrm_order_lead()


@pytest.fixture
def paid_order_without_lead(user, course, factory):
    return factory.order(user=user, course=course, is_paid=True, author=user)


@pytest.fixture
def paid_order_with_lead(user, course, factory, amocrm_lead):
    return factory.order(user=user, course=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)


@pytest.fixture
def not_paid_order_without_lead(factory, user, course):
    return factory.order(user=user, course=course, is_paid=False, author=user)


@pytest.fixture
def not_paid_order_with_lead(factory, user, course, amocrm_lead):
    return factory.order(user=user, course=course, is_paid=False, author=user, amocrm_lead=amocrm_lead)


@pytest.fixture
def returned_order_with_lead(factory, user, course, amocrm_lead):
    order = factory.order(user=user, course=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)
    order.set_not_paid()
    return order


def test_create_if_no_lead_not_paid(not_paid_order_without_lead, mock_create_amocrm_lead):
    """Поступил новый открытый заказ, аналогичной сделки в Амо еще нет - создается новая сделка в Амо"""
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_create_amocrm_lead.assert_called_once_with(kwargs=dict(order_id=not_paid_order_without_lead.id), countdown=1)


def test_update_if_with_lead_not_paid(not_paid_order_with_lead, mock_update_amocrm_lead):
    """Сделка уже есть в АмоБ обновился заказ в лмс - обновляем сделку в Амо"""
    AmoCRMOrderPusher(order=not_paid_order_with_lead)()

    mock_update_amocrm_lead.assert_called_once_with(kwargs=dict(order_id=not_paid_order_with_lead.id), countdown=1)


def test_update_if_with_lead_paid(paid_order_with_lead, mock_push_existing_order_to_amocrm):
    """Поступила оплата заказа - пушим весь заказ (обновляем Сделку и создаем Покупку)"""
    AmoCRMOrderPusher(order=paid_order_with_lead)()

    mock_push_existing_order_to_amocrm.assert_called_once_with(kwargs=dict(order_id=paid_order_with_lead.id), countdown=1)


def test_update_if_with_lead_returned(returned_order_with_lead, mock_push_existing_order_to_amocrm):
    """Заказ возвращен - пушим весь заказ (обновляем Сделку и удаляем Покупку)"""
    AmoCRMOrderPusher(order=returned_order_with_lead)()

    mock_push_existing_order_to_amocrm.assert_called_once_with(kwargs=dict(order_id=returned_order_with_lead.id), countdown=1)


@pytest.mark.usefixtures("not_paid_order_with_lead")
def test_update_not_paid_order_linked_to_existing_lead(not_paid_order_without_lead, mock_update_amocrm_lead, amocrm_lead):
    """Поступил новый открытый заказ, но аналогичная сделка уже есть в Амо - привязываем сделку к текущему заказу и обновляем сделку в Амо"""
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    assert not_paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_update_amocrm_lead.assert_called_once_with(kwargs=dict(order_id=not_paid_order_without_lead.id), countdown=1)


@pytest.mark.usefixtures("not_paid_order_with_lead")
def test_update_paid_order_linked_to_existing_lead(paid_order_without_lead, amocrm_lead, mock_push_existing_order_to_amocrm):
    """Поступила оплата по заказу, но соответствующая сделка привязана к другому аналогичному заказу - привязываем сделку к текущему заказу и пушим в Амо"""
    AmoCRMOrderPusher(order=paid_order_without_lead)()

    assert paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_push_existing_order_to_amocrm.assert_called_once_with(kwargs=dict(order_id=paid_order_without_lead.id), countdown=1)


@pytest.mark.usefixtures("returned_order_with_lead")
def test_update_linked_to_existing_lead_from_returned_order_(paid_order_without_lead, amocrm_lead, mock_push_existing_order_to_amocrm):
    """
    Поступила оплата по заказу, но соответствующая сделка привязана к другому аналогичному возвращенному заказу -
    привязываем сделку к текущему заказу и пушим в Амо
    """
    AmoCRMOrderPusher(order=paid_order_without_lead)()

    assert paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_push_existing_order_to_amocrm.assert_called_once_with(kwargs=dict(order_id=paid_order_without_lead.id), countdown=1)


def test_not_push_if_author_not_equal_to_user(not_paid_order_without_lead, another_user, mock_push_lead, mock_push_order):
    not_paid_order_without_lead.setattr_and_save("author", another_user)

    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_push_lead.assert_not_called()
    mock_push_order.assert_not_called()


def test_not_push_if_free_order(not_paid_order_without_lead, mock_push_lead, mock_push_order):
    not_paid_order_without_lead.setattr_and_save("price", Decimal(0))

    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_push_lead.assert_not_called()
    mock_push_order.assert_not_called()


@pytest.mark.usefixtures("paid_order_with_lead")
def test_not_push_if_there_is_already_paid_order(not_paid_order_without_lead, mock_push_lead, mock_push_order):
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_push_lead.assert_not_called()
    mock_push_order.assert_not_called()


@pytest.mark.usefixtures("not_paid_order_with_lead")
def test_child_service_gets_order_with_linked_lead(not_paid_order_without_lead, amocrm_lead, mocker):
    """
    Поступил новый заказ, но есть аналогичный неоплаченный заказ с открытой сделкой -
    сделка привязывается к новому заказу, и обновляется в Амо, чтобы была указана актуальная стоимость и время создания
    """
    mock_updater_init = mocker.patch("amocrm.services.orders.order_lead_updater.AmoCRMOrderLeadUpdater.__init__", return_value=None)
    mock_update = mocker.patch("amocrm.services.orders.order_lead_updater.AmoCRMOrderLeadUpdater.__call__")

    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    assert not_paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_updater_init.assert_called_once_with(amocrm_lead=amocrm_lead)
    mock_update.assert_called_once()


def test_fail_create_paid_order_without_lead(paid_order_without_lead):
    with pytest.raises(AmoCRMOrderPusherException, match="Cannot push paid or unpaid order without existing lead"):
        AmoCRMOrderPusher(order=paid_order_without_lead)()