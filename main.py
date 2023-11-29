from collections import UserDict
from datetime import datetime


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass


class Name(Field):
    pass


class Phone(Field):
    def validate(self, value):
        if not (isinstance(value, str) and len(value) == 10 and value.isdigit()):
            raise ValueError("Invalid phone number format")


class Birthday(Field):
    def validate(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid birthday format. Please use YYYY-MM-DD")


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone
                break
        else:
            raise ValueError("Phone number does not exist in the record")

    def get_phones(self):
        return [str(phone) for phone in self.phones]

    def find_phone(self, phone):
        found_phones = [p for p in self.phones if str(p) == phone]
        return found_phones[0] if found_phones else None

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_remaining = (next_birthday - today).days
            return days_remaining
        return None

    def __str__(self):
        return f"Contact name: {self.name}, phones: {', '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.page_size = 5
        self.current_page = 1

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __iter__(self):
        return self.record_iterator()

    def get_page(self, page_number):
        start_index = (page_number - 1) * self.page_size
        end_index = start_index + self.page_size
        return list(self.data.values())[start_index:end_index]

    def record_iterator(self):
        for record in self.data.values():
            yield str(record)

    def get_n_records(self, n):
        records = []
        for _ in range(n):
            try:
                record = next(self.record_iterator())
                records.append(record)
            except StopIteration:
                break
        return records


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return f"Error: {str(e)}"

    return wrapper


contacts = AddressBook()


@input_error
def add_contact(name, phone, birthday=None):
    contact = contacts.find(name)
    if contact:
        contact.add_phone(phone)
    else:
        record = Record(name, birthday)
        record.add_phone(phone)
        contacts.add_record(record)
    return f"Contact {name} added with phone {phone}"


@input_error
def delete_contact(name):
    contact = contacts.find(name)
    if contact:
        contacts.delete(name)
        return f"Contact {name} deleted"
    else:
        return f"Contact {name} not found"


@input_error
def get_phone(name):
    contact = contacts.find(name)
    if contact and contact.phones:
        return f"Phone numbers for {name}: {', '.join(contact.get_phones())}"
    else:
        raise ValueError(f"Contact {name} not found")


@input_error
def change_phone(name, old_phone, new_phone):
    contact = contacts.find(name)
    if contact:
        contact.edit_phone(old_phone, new_phone)
    else:
        raise ValueError(f"Contact {name} not found")


@input_error
def show_all():
    page = contacts.get_page(contacts.current_page)
    result = "\n".join(str(record) for record in page)
    return f"Page {contacts.current_page}:\n{result}"


@input_error
def show_n_records(n):
    records = contacts.get_n_records(n)
    result = "\n".join(records)
    return f"{n} records:\n{result}"


def main():
    while True:
        command = input("Enter command: ").lower()

        if command == "hello":
            print("How can I help you?")
        elif command.startswith("add"):
            _, name, phone, *birthday = command.split()
            birthday = birthday[0] if birthday else None
            print(add_contact(name, phone, birthday))
        elif command.startswith("delete"):
            _, name = command.split()
            print(delete_contact(name))
        elif command.startswith("change"):
            _, name, old_phone, new_phone = command.split()
            print(change_phone(name, old_phone, new_phone))
        elif command.startswith("phone"):
            _, name = command.split()
            print(get_phone(name))
        elif command.startswith("show all"):
            print(show_all())
        elif command.startswith("show n records"):
            _, n = command.split()
            n = int(n)
            print(show_n_records(n))
        elif command in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    main()
