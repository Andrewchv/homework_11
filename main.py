from collections import UserDict
from datetime import datetime
from shlex import split


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
    def __str__(self):
        return str(self.value)


class Phone(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate_phone(new_value)
        self._value = new_value

    def validate_phone(self, value):
        if value is not None and (not isinstance(value, str) or not (len(value) == 10 and value.isdigit())):
            raise ValueError("Invalid phone number format")


class Birthday(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate_birthday(new_value)
        self._value = datetime.strptime(new_value, '%Y-%m-%d')
    
    def validate_birthday(self, value):
        if value is not None:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid birthday format. Please use YYYY-MM-DD")
    
    def __str__(self):
        return str(self.value.strftime('%Y-%m-%d'))


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def find_phone(self, phone):
        found_phones = [p.value for p in self.phones if str(p) == phone]
        return found_phones[0] if found_phones else None

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone.value) == old_phone:
                phone.value = new_phone
                break
        else:
            raise ValueError("Phone number does not exist in the record")

    def get_phones(self):
        return [str(phone.value) for phone in self.phones]

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
        phones_str = ', '.join(str(phone.value) for phone in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.page_size = 5
        self.current_page = 1

    def add_record(self, record):
        if record.name.value.lower() in (existing_record.name.value.lower() for existing_record in self.data.values()):
            existing_record = next(existing_record for existing_record in self.data.values() if existing_record.name.value.lower() == record.name.value.lower())
            existing_record.phones.extend(record.phones)
        else:
            self.data[record.name.value] = record

    def find(self, name):
        name_lower = name.lower()
        return next((record for record in self.data.values() if record.name.value.lower() == name_lower), None)

    def delete(self, name):
        record = next((record for record in self.data.values() if record.name.value.lower() == name.lower()), None)
        if record:
            del self.data[record.name.value]

    def change_phone(self, name, old_phone, new_phone):
        name_lower = name.lower()
        record = self.find(name_lower)
        if record:
            record.edit_phone(old_phone, new_phone)
        else:
            raise ValueError(f"Contact {name} not found")

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
def delete_contact(command):
    name = command[1]
    contacts.delete(name)
    return f"Contact {name} deleted"


@input_error
def change_phone(name, new_phone):
    contact = contacts.find(name)
    if contact:
        contact.edit_phone(contact.phones[0].value, new_phone)
        return f"Phone number for {name} changed to {new_phone}"
    else:
        raise ValueError(f"Contact {name} not found")


@input_error
def get_phones(command):
    name = split(command)[1]
    contact = next((record for record in contacts.data.values() if record.name.value.lower() == name.lower()), None)
    if contact and contact.phones:
        return f"Phone numbers for {contact.name.value}: {', '.join(map(str, contact.get_phones()))}"
    else:
        raise ValueError(f"Contact {name.capitalize()} not found")


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


@input_error
def days_to_birthday(command):
    name = command.split()[1]
    contact = contacts.find(name)
    if contact and contact.birthday:
        days_remaining = contact.days_to_birthday()
        return f"Days to {contact.name.value}'s birthday: {days_remaining} days"
    elif contact and not contact.birthday:
        return f"{contact.name.value} doesn't have a birthday set."
    else:
        raise ValueError(f"Contact {name} not found")


def main():
    while True:
        command = input("Enter command: ").lower()

        if command == "hello":
            print("How can I help you?")
        elif command.startswith("add"):
            _, name, *phones = command.split(", ")
            print(add_contact(name, *phones))
        elif command.startswith("delete"):
            name = command.split()
            print(delete_contact(name))
        elif command.startswith("change"):
            _, name, _, new_phone = command.split(", ")
            print(change_phone(name, new_phone))
        elif command.startswith("phone"):
            print(get_phones(command))
        elif command.startswith("show all"):
            print(show_all())
        elif command.startswith("show n records"):
            n = int(command.split()[3])
            print(show_n_records(n))
        elif command.startswith("days_to_birthday"):
            print(days_to_birthday(command))
        elif command in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    main()
