from protzilla.utilities import name_to_title


def test_name_to_title():
    # Test if function correctly transforms "ms_test_this" to "MS Test This"
    assert name_to_title("ms_test_this") == "MS Test This"
    assert name_to_title("MS_test_this") == "MS Test This"

    # Test if function correctly capitalizes the first letter of each word
    assert name_to_title("hello_world") == "Hello World"
    assert name_to_title("another_test case") == "Another Test Case"
    assert name_to_title("ANOTHER TEST cASe") == "Another Test Case"
