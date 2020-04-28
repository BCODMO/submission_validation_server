from goodtables import check

# Module API


@check("latitude-bounds", type="custom", context="body")
class LatitudeBounds(object):

    # Public

    def __init__(self, constraint, **options):
        self.__constraint = constraint

    def check_row(self, errors, cells, row_number):
        print("CECHKING LAT BOUNDS")

        for cell in cells:
            if cell["header"] == self.__constraint:
                # Check constraint
                try:
                    assert cell["value"] > -90 and cell["value"] < 90
                except Exception:
                    message = f"Latitude column {self.__constraint} at row {row_number} is not between -90 and 90"
                    return errors.append(
                        {
                            "code": "latitude-bounds",
                            "message": message,
                            "row-number": row_number,
                            "column-number": cell["number"],
                        }
                    )
