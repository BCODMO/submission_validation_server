from goodtables import check

# Module API


@check("longitude-bounds", type="custom", context="body")
class LongitudeBounds(object):

    # Public

    def __init__(self, constraint, **options):
        self.__constraint = constraint

    def check_row(self, errors, cells, row_number):
        print("CECHKING LON BOUNDS")

        for cell in cells:
            if cell["header"] == self.__constraint:
                # Check constraint
                try:
                    assert cell["value"] > -180 and cell["value"] < 180
                except Exception:
                    message = f"Longitude column {self.__constraint} at row {row_number} is not between -180 and 180"
                    return errors.append(
                        {
                            "code": "longitude-bounds",
                            "message": message,
                            "row-number": row_number,
                            "column-number": cell["number"],
                        }
                    )
