from dataset.distribution import main_procurement_category


def test_general():
    main_procurement_category.add_item("")
    main_procurement_category.add_item("")
    assert main_procurement_category.get_result() == 2
