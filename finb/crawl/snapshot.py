from finb.crawl.web_driver import make_driver

# https://stackoverflow.com/questions/17975471/selenium-with-scrapy-for-dynamic-page

def get_company_snapshot(symbol):
    url = f"http://ra.vcsc.com.vn/?lang=vi-VN&ticker={symbol}"

    driver = make_driver()
    driver.get(url)

    snapshot_div = driver.find_element_by_id("FinancialOverview")
    div1_span5s = snapshot_div.find_elements_by_class_name("span5")


    keys = [
        "Giá tham chiếu",
        "Mở cửa",
        "Cao nhất",
        "Giá thấp nhất",
        "Đóng cửa",
        "KL",
        "GD ròng NĐTNN",
        "Room khối ngoại",
        "Tỷ lệ nắm giữ hiện tại (%)",
        "Tỷ lệ nắm giữ tối đa (%)",
        "Thấp nhất 52 tuần",
        "Cao nhất 52 tuần",
        "EPS 4 quí gần nhất",
        "P/E",
        "P/B",
        "KLGD KL TB 10 phiên",
        "KLCP đang lưu hành",
        "Vốn hóa"
    ]
    values = []

    kidx = 0
    for div_elem in div1_span5s:
        div_home_block = div_elem.find_element_by_class_name("home-block2")
        p_elems = div_home_block.find_elements_by_tag_name("p")
        for elem in p_elems:
            label = elem.find_element_by_tag_name("label")
            value = label.text.strip()

            if "." in value:
                value = value.replace(".", "")
                value = float(value)
            elif "," in value:
                value = value.replace(",", ".")
                value = float(value)
            else:
                value = None

            if keys[kidx] in {'Giá tham chiếu',"Mở cửa", "Cao nhất", "Giá thấp nhất", 'Đóng cửa', 'Thấp nhất 52 tuần', 'Cao nhất 52 tuần', 'EPS 4 quí gần nhất'}:
                value = value/1000
            if keys[kidx] == 'Vốn hóa':
                value = value * 1e9
            values.append(value)
            kidx += 1
    ret = dict(zip(keys, values))

    return ret


if __name__ == "__main__":
    print(get_company_snapshot("ABC"))
