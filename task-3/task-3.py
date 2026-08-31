from abc import ABC, abstractmethod
from enum import Enum
from contextlib import suppress

class ItemStatus(Enum):
    AVAILABLE = 1
    CHECKED_OUT = 2
    LOST = 3

class LibraryItem(ABC):
    _registry = {}

    @classmethod
    def register(cls, type_name: str, subclass: 'LibraryItem') -> None:
        cls._registry[type_name] = subclass

    @classmethod
    def from_dict(cls, data: dict) -> 'LibraryItem':
        type_name = data.get('type')
        if not type_name:
            raise ValueError("Missing 'type' field")
        subclass = cls._registry.get(type_name)
        if not subclass:
            raise ValueError(f"Unknown item type: {type_name}")

        title = data.get('title')
        if not title:
            raise ValueError("Missing 'title' field")
        status_str = data.get('status', 'AVAILABLE')
        try:
            status = ItemStatus[status_str]
        except KeyError as e:
            raise ValueError(f"Invalid status: {status_str}") from e

        extra = {k: v for k, v in data.items() if k not in ('type', 'status', 'title')}
        return subclass(title=title, status=status, **extra)

    @staticmethod
    def check_isbn(isbn: str) -> bool:
        num_in_isbn = "".join(i for i in isbn if i.isdigit())
        if len(num_in_isbn) != 13:
            return False
        total = sum(int(value) if idx % 2 == 0 else int(value) * 3
                    for idx, value in enumerate(num_in_isbn[:-1]))
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(num_in_isbn[-1])

    def __init__(self, title: str, status: ItemStatus = ItemStatus.AVAILABLE):
        self._title = title
        self._status = status

    def checkout(self):
        if self._status != ItemStatus.AVAILABLE:
            raise ValueError(f"Item '{self._title}' cannot be checked out")
        self._status = ItemStatus.CHECKED_OUT

    def return_item(self):
        if self._status != ItemStatus.CHECKED_OUT:
            raise ValueError(f"Item '{self._title}' is not checked out")
        self._status = ItemStatus.AVAILABLE

    def mark_lost(self):
        self._status = ItemStatus.LOST

    def __lt__(self, other):
        if not isinstance(other, LibraryItem):
            return NotImplemented
        return self._title < other._title

    def __repr__(self):
        return f"{self._title} ({self.item_type()}) , status:{self._status.name}"

    def __str__(self):
        return f"{self._title} ({self.item_type()}) - {self._status.name}"

    @abstractmethod
    def to_db_string(self) -> str:
        pass

    @abstractmethod
    def loan_period(self) -> int:
        pass

    @abstractmethod
    def item_type(self) -> str:
        pass

    def get_name(self) -> str:
        return self._title

    def get_state(self) -> ItemStatus:
        return self._status

class Book(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, author="", isbn=""):
        super().__init__(title, status)
        self.author = author
        self.isbn = isbn

    def loan_period(self) -> int:
        return 21

    def item_type(self) -> str:
        return "Book"

    def to_db_string(self):
        return f"type=Book|title={self._title}|author={self.author}|isbn={self.isbn}|status={self._status.name}"

class DVD(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, director=""):
        super().__init__(title, status)
        self.director = director

    def loan_period(self) -> int:
        return 5

    def item_type(self) -> str:
        return "DVD"

    def to_db_string(self):
        return f"type=DVD|title={self._title}|director={self.director}|status={self._status.name}"

class Magazine(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, issue=""):
        super().__init__(title, status)
        self.issue = issue

    def loan_period(self) -> int:
        return 14

    def item_type(self) -> str:
        return "Magazine"

    def to_db_string(self):
        return f"type=Magazine|title={self._title}|issue={self.issue}|status={self._status.name}"

class AudioBook(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, narrator="", duration=0):
        super().__init__(title, status)
        self.narrator = narrator
        self.duration = duration

    def loan_period(self) -> int:
        return 14

    def item_type(self) -> str:
        return "AudioBook"

    def to_db_string(self):
        return f"type=AudioBook|title={self._title}|narrator={self.narrator}|duration={self.duration}|status={self._status.name}"

class Database:
    def __init__(self, file):
        self._txt_file = file

    def read_from_file(self):
        try:
            with open(self._txt_file) as f:
                items = [line.strip() for line in f if line.strip()]
            return items
        except FileNotFoundError:
            return []

    def write_to_file(self, line):
        with suppress(FileNotFoundError):
            with open(self._txt_file, 'r') as f:
                content = f.read()
            if content and not content.endswith('\n'):
                with open(self._txt_file, 'a') as f:
                    f.write('\n' + line + '\n')
                return
        with open(self._txt_file, 'a') as f:
            f.write(line + '\n')

    def save(self, items):
        with open(self._txt_file, 'w') as f:
            for item in items:
                f.write(item.to_db_string() + '\n')

class Library:
    def __init__(self):
        self._database = Database('database.txt')
        LibraryItem.register('Book', Book)
        LibraryItem.register('DVD', DVD)
        LibraryItem.register('Magazine', Magazine)
        self._items = self._load_items_from_file()

    def _load_items_from_file(self):
        list_of_items = []
        for line in self._database.read_from_file():
            if not line.strip():
                continue
            item_dict = {}
            for part in line.split("|"):
                if '=' not in part:
                    continue
                key, value = part.split("=", 1)
                item_dict[key.strip()] = value.strip()
            list_of_items.append(LibraryItem.from_dict(item_dict))
        return list_of_items

    def add_item(self, other):
        if not isinstance(other, LibraryItem):
            raise ValueError(f"{other} not an instance of LibraryItem")
        existing = self.find_by_title(other.get_name())
        if existing is not None:
            raise ValueError(f"Item with title '{other.get_name()}' already exists")
        self._items.append(other)

    def find_by_title(self, title):
        return next((item for item in self._items if item.get_name().lower() == title.lower()), None)

    def checkout(self, title):
        item = self.find_by_title(title)
        if item is None:
            raise ValueError(f"Item '{title}' not found")
        item.checkout()

    def return_item(self, title):
        item = self.find_by_title(title)
        if item is None:
            raise ValueError(f"Item '{title}' not found")
        item.return_item()

    def mark_lost(self, title):
        item = self.find_by_title(title)
        if item is None:
            raise ValueError(f"Item '{title}' not found")
        item.mark_lost()

    def list_available(self):
        return [item for item in self._items if item.get_state() == ItemStatus.AVAILABLE]

    def save(self):
        self._items = [item for item in self._items if isinstance(item, LibraryItem)]
        self._database.save(self._items)

LibraryItem.register('Book', Book)
LibraryItem.register('DVD', DVD)
LibraryItem.register('Magazine', Magazine)
LibraryItem.register('AudioBook', AudioBook)

if __name__ == "__main__":
    a = Book("Dune")
    b = DVD("Adventure time")
    c = Magazine("Ball Magazine")

    print(a)
    a.checkout()
    print(a)

    items = [a, b, c]
    print(sorted(items))

    book_data = {
        "type": "Book",
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "978-0-441-01359-3",
        "status": "AVAILABLE"
    }
    dvd_data = {
        "type": "DVD",
        "title": "Inception",
        "director": "Christopher Nolan",
        "status": "CHECKED_OUT"
    }
    magazine_data = {
        "type": "Magazine",
        "title": "National Geographic",
        "issue": "2026-08",
        "status": "AVAILABLE"
    }

    book = LibraryItem.from_dict(book_data)
    dvd = LibraryItem.from_dict(dvd_data)
    mag = LibraryItem.from_dict(magazine_data)

    print(book)
    print(dvd)
    print(mag)

    print(book.author)
    print(book.isbn)
    print(dvd.director)
    print(mag.issue)

    dvd.return_item()
    print(dvd)

    book.mark_lost()
    try:
        book.checkout()
    except ValueError as e:
        print("Caught expected error:", e)

    print("ISBN valid?", LibraryItem.check_isbn("978-0-441-01359-3"))

    lib = Library()

    new_book = Book("Neuromancer3", author="William Gibson", isbn="9780441013593")
    lib.add_item(new_book)
    print("Added:", new_book)

    found = lib.find_by_title("neuromancer3")
    print("Found:", found)

    available = lib.list_available()
    print("Available items:", [item.get_name() for item in available])

    lib.save()
    lib2 = Library()
    found2 = lib2.find_by_title("Neuromancer3")
    print("Reloaded status:", found2.get_state().name if found2 else "Not found")

    print("ISBN valid (9780441013593):", LibraryItem.check_isbn("9780441013593"))
    print("ISBN valid (1234567890123):", LibraryItem.check_isbn("1234567890123"))

    bad_data = {"type": "Book", "title": "Bad", "status": "UNKNOWN"}
    try:
        LibraryItem.from_dict(bad_data)
    except ValueError as e:
        print("Expected error:", e)

    ab = AudioBook("Dune Audiobook", narrator="Scott Brick", duration=120)
    lib.add_item(ab)

    audio_data = {
        "type": "AudioBook",
        "title": "1984 Audiobook",
        "narrator": "Simon Prebble",
        "duration": 90,
        "status": "AVAILABLE"
    }
    ab_from_dict = LibraryItem.from_dict(audio_data)
    print("AudioBook from dict:", ab_from_dict)