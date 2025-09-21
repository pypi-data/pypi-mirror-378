
import gi
gi.require_version('Gio', '2.0')
gi.require_version('GioUnix', '2.0')
gi.require_version('Notify', '0.7')
from gi.repository import Notify


def _notify(title: str, message: str) -> None:
    Notify.init(title)
    Notify.Notification.new(message).show()
