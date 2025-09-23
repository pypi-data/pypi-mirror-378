import muse.muse_lang as ml
import muse.sample as sample
import middata_sample as m_sample

def test_code(code):
    print(ml.ast_check(code))
    result = ml.trial(code)
    if result['code'] == 'SUCCESS':
        print(result['data'])
        if 'error_msg' in result and result['error_msg'] != '':
            print(result['error_msgs'])
    else:
        print(result['error_msgs'])


def test_all():
    i = 1
    for s in sample.demos:
        print(f'-------demo{i}--------')
        test_code(s)
        i += 1

if __name__ == '__main__':
    # test_all()
    # print(ml.get_ds().get_datasource_name())
    # test_code(sample.demo7)
    print(ml.ast_check(m_sample.demo1))
    print(ml.indicators_check(m_sample.demo7))
    # result = ml.trial(
    #     '''七日年化收益率数据 = 指标('产品每日指标', ['产品代码', '产品名称', '日期', '七日年化收益率'], {'PORT_TAGS': '宁薪普通封闭式', 'START_DATE': '2025-04-30', 'END_DATE': '2025-04-30'})''')
    # print(result)