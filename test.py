import argparse

from financial_reports.request_info import QueryParamter, MopsRequestInfo

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Test regarding of functions')
    parser.add_argument('-t', '--test', type=str, dest='test')
    args = parser.parse_args()

    if args.test == 'test-query-parameter':
        param = QueryParamter('2330', 2020)
        print(param)

    elif args.test == 'test-request-info':
        request_info = MopsRequestInfo('cash_flow', '2330', 2020)
        print(request_info)

    elif args.test == 'test':
        pass

    else:
        print('Unknow endpoint: {}'.format(args.test))