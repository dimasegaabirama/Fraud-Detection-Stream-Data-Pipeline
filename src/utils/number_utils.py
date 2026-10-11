def validate_number(attr: str, data):
    validation = []
    for key, values in data.items():
        if values is None:
            continue
        else:
            value = getattr(values, attr)
        
        if len(validation) == 0:
            validation.append(value)
        else:
            if value >= validation[-1]:
                raise ValueError(f"{key} threshold must be less than the previous")
            validation.append(value)

if __name__ == "__main__":
    pass