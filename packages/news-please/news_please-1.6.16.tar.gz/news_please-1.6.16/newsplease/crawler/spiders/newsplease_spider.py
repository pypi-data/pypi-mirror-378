from abc import abstractmethod, ABC


class NewspleaseSpider(ABC):
    """
    Abstract base class for newsplease spiders.
    Defines methods that should be inherited by subclasses
    """

    @staticmethod
    @abstractmethod
    def supports_site(url: str, check_certificate: bool = True) -> bool:
        """
        Determines if this spider works on the given URL.

        :param str url: The url to test
        :param bool check_certificate: The url to test
        :return bool:
        """
        pass

    @staticmethod
    def has_urls_to_scan(url: str, check_certificate: bool = True) -> bool:
        """
        Determines if this spider has any URLs to scan.

        :param str url: The url to test
        :param bool check_certificate:
        :return bool:
        """
        return True
