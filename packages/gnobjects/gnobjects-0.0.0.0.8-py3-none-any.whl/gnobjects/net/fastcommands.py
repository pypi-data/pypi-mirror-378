from typing import Optional, Union, List

from KeyisBTools.models.serialization import SerializableType

from .objects import GNResponse, FileObject, CORSObject



class GNFastCommand(GNResponse):
    """
    # Быстрый ответ
    """
    def __init__(self,
                 payload: Optional[SerializableType] = None,
                 files: Optional[Union[str, FileObject, List[FileObject]]] = None,
                 cors: Optional[CORSObject] = None):

        command = getattr(self, "cls_command", None)
        if command is None:
            command = 'gn:code-error:undefined'

        super().__init__(command=command, payload=payload, files=files, cors=cors)


class AllGNFastCommands:
    class ok(GNFastCommand):
        """
        # Корректный ответ
        """
        cls_command = True
       
        
    class UnprocessableEntity(GNFastCommand):
        """
        # Некорректные данные
        Ошибка указывает, что сервер понял запрос, но не может его обработать из-за неверного содержания. 
        Пример: передан payload с правильной структурой, но поля содержат некорректные значения (например, строка вместо числа).
        Используется, когда данные формально корректны, но нарушают бизнес-логику.
        """
        cls_command = "gn:origin:422"


    class BadRequest(GNFastCommand):
        """
        # Неправильный синтаксис url или параметров
        Сервер не может понять запрос из-за ошибок в структуре или параметрах. 
        Пример: отсутствует обязательный параметр или указан некорректный формат даты.
        Часто используется при валидации входных данных на уровне запроса.
        """
        cls_command = "gn:origin:400"


    class Forbidden(GNFastCommand):
        """
        # Доступ запрещён, даже при наличии авторизации
        Клиент аутентифицирован, но не имеет прав для выполнения действия. 
        Пример: пользователь вошёл в систему, но пытается изменить чужие данные.
        Используется для разграничения прав доступа.
        """
        cls_command = "gn:origin:403"


    class Unauthorized(GNFastCommand):
        """
        # Требуется авторизация
        Ошибка возвращается, если запрос требует входа, но клиент не предоставил или предоставил неверные данные авторизации. 
        Пример: отсутствует заголовок Authorization или токен недействителен.
        Используется для защиты закрытых API-эндпоинтов.
        """
        cls_command = "gn:origin:401"


    class NotFound(GNFastCommand):
        """
        # Ресурс не найден
        Запрошенный объект или путь не существует на сервере. 
        Пример: попытка получить пользователя с несуществующим ID.
        Часто используется для API-ответов на невалидные ссылки.
        """
        cls_command = "gn:origin:404"


    class MethodNotAllowed(GNFastCommand):
        """
        # Метод запроса не поддерживается данным ресурсом
        Ресурс существует, но используемый gn-метод недопустим. 
        Пример: к ресурсу разрешён только GET, а клиент делает POST.
        Используется для ограничения набора действий над конкретными ресурсами.
        """
        cls_command = "gn:origin:405"


    class Conflict(GNFastCommand):
        """
        # Конфликт состояния ресурса (например, дубликат)
        Возникает, когда операция не может быть выполнена из-за противоречия с текущим состоянием ресурса. 
        Пример: попытка зарегистрировать пользователя с уже существующим email.
        Используется для предотвращения логических коллизий.
        """
        cls_command = "gn:origin:409"


    class InternalServerError(GNFastCommand):
        """
        # Внутренняя ошибка сервера
        Сервер столкнулся с непредвиденной ситуацией, которая не позволяет выполнить запрос. 
        Пример: необработанное исключение в коде приложения.
        Используется как универсальная ошибка для внутренних сбоев.
        """
        cls_command = "gn:origin:500"


    class NotImplemented(GNFastCommand):
        """
        # Метод или функционал ещё не реализован
        Сервер распознаёт запрос, но не поддерживает требуемый функционал. 
        Пример: метод API описан в документации, но ещё не реализован.
        Используется для обозначения незавершённых частей системы.
        """
        cls_command = "gn:origin:501"


    class BadGateway(GNFastCommand):
        """
        # Ошибка шлюза или прокси при обращении к апстриму
        Промежуточный сервер получил некорректный ответ от апстрим-сервера. 
        Пример: API-шлюз обращается к backend, но тот вернул ошибку.
        """
        cls_command = "gn:origin:502"


    class ServiceUnavailable(GNFastCommand):
        """
        # Сервис временно недоступен
        Сервер не может обработать запрос из-за перегрузки или обслуживания. 
        Пример: база данных недоступна или сервис в режиме обновления.
        Используется для сигнализации о временных проблемах.
        """
        cls_command = "gn:origin:503"


    class GatewayTimeout(GNFastCommand):
        """
        # Таймаут при обращении к апстриму
        Прокси или шлюз не дождался ответа от вышестоящего сервера в установленный срок. 
        Пример: запрос к медленному backend-сервису превысил лимит времени.
        Используется для контроля SLA и таймаутов в распределённых системах.
        """
        cls_command = "gn:origin:504"

    class DnsDomainAccessDenied(GNFastCommand):
        """
        # DNS Доступ к домену запрещён
        Запрос был отклонён из-за настроек доступа.
        """
        cls_command = "gn:origin:601"


    class DnsInvalidVerificationAlgorithm(GNFastCommand):
        """
        # DNS Некорректный алгоритм подписи
        Сервер указал неподдерживаемый или неверный алгоритм подписи при проверке доступа к домену.
        """
        cls_command = "gn:origin:602"


    class DnsServerKeyNotFound(GNFastCommand):
        """
        # DNS Не удалось получить ключ сервера
        При попытке разрешить домен отсутствует ключ сервера для верификации подписи.
        Пример: запись в реестре доменов повреждена или отсутствует.
        """
        cls_command = "gn:origin:603"


    class DnsInvalidSignature(GNFastCommand):
        """
        # DNS Некорректная подпись
        Полученная подпись при попытке разрешить домен не прошла криптографическую проверку.
        Пример: данные были подменены в процессе передачи.
        """
        cls_command = "gn:origin:604"


    class DnsDomainDecryptionError(GNFastCommand):
        """
        # DNS Ошибка при расшифровке запроса
        Во время обработки запроса для разрешения домена произошла ошибка при расшифровке.
        Пример: клиент использовал неверный ключ или формат данных.
        """
        cls_command = "gn:origin:605"


    class DnsDomainNotFound(GNFastCommand):
        """
        # DNS Запрашиваемый домен не найден
        Домен отсутствует в системе или не имеет действующих записей.
        Пример: опечатка в имени или удалённая зона.
        """
        cls_command = "gn:origin:606"


    class DnsSenderDomainMismatch(GNFastCommand):
        """
        # DNS Несоответствие домена отправителя
        Проверка показала, что указанный отправитель не соответствует ожидаемому домену.
        Пример: подмена адреса в заголовках.
        """
        cls_command = "gn:origin:607"


    class DnsDomainResolutionDenied(GNFastCommand):
        """
        # DNS Не удалось получить доступ к разрешению домена
        Процесс разрешения домена был отклонён системой.
        """
        cls_command = "gn:origin:608"



globals().update({
    name: obj
    for name, obj in AllGNFastCommands.__dict__.items()
    if isinstance(obj, type) and issubclass(obj, GNFastCommand)
})







