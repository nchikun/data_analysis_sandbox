import pandas as pd


class ContingencyTableAnalysis:
    """
    分割表の統計解析モジュール。

    Parameters
    ----------
    df_cont_tb: pd.DataFrame
        解析元の分割表。

    const_law: 'all' or 'raw_all' or 'col_all' or 'none'
        分割表中の確定した値の箇所。
        'all': 行列和が確定的
        'raw_all': 行和が確定的
        'col_all': 列和が確定的
        'none': 全セルが確定的
    """

    CONST_LAWS = ['all', 'raw_all', 'col_all', 'none']

    def __init__(self, df_cont_tb: pd.DataFrame, const_law='all'):
        # exception
        if const_law not in self.CONST_LAWS:
            raise AttributeError("const_law must be inputted 'all' or 'raw_all' or 'col_all', or 'none'.")

        # initializer
        self.df_cont_tb = df_cont_tb
        self.const_law = const_law

    def sum_all(self, row_name: str, col_name: str) -> pd.DataFrame:
        """
        TODO
        ・データチェックの例外を設ける
        """
        df_add_sum = self.df_cont_tb.copy()
        df_add_sum[col_name] = df_add_sum.sum(axis='columns')
        df_add_sum = self.sum_row(df_add_sum, row_name)
        return df_add_sum

    # Private
    @staticmethod
    def sum_row(df: pd.DataFrame, row_name: str) -> pd.DataFrame:
        df_result = df.copy()
        df_row_sum = pd.DataFrame(df.sum(axis='index')).T
        df_row_sum.index = [row_name]
        return df_result.append(df_row_sum)
