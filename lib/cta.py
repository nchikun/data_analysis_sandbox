import scipy.stats as stats
import pandas as pd


class ContingencyTableAnalysis:
    """
    分割表の統計解析モジュール。

    Parameters
    ----------
    df_cont_tb: pd.DataFrame
        解析元の分割表。

    sum_raw_name: str, default 'raw_all'
        分割表の行和の項目名。

    sum_col_name: str, default 'col_all'
        分割表の列和の項目名。

    const_law: 'all' or 'raw_all' or 'col_all' or 'none'
        分割表中の確定した値の箇所。
        'all': 行列和が確定的
        'raw_all': 行和が確定的
        'col_all': 列和が確定的
        'none': 全セルが確定的
    """

    _CONST_LAWS = ['all', 'raw_all', 'col_all', 'none']
    _ERROR_CONST_LAW = "const_law must be inputted 'all' or 'raw_all' or 'col_all', or 'none'."

    def __init__(self,
                 df_cont_tb: pd.DataFrame,
                 sum_raw_name='raw_all',
                 sum_col_name='col_all',
                 const_law='all'):
        if const_law not in self._CONST_LAWS:
            raise AttributeError(self._ERROR_CONST_LAW)

        self.df_cont_tb = df_cont_tb
        self.sum_raw_name = sum_raw_name
        self.sum_col_name = sum_col_name
        self.const_law = const_law

    def sum_all(self) -> pd.DataFrame:
        """
        行和、列和、行列和を計算したDataFrameを返す。

        Returns
        -------
        df_add_sum: pd.DataFrame
            初期化引数df_cont_tbに対して行和、列和、行列和を計算したDataFrame。
        """
        df_add_sum = self.df_cont_tb.copy()
        df_add_sum[self.sum_col_name] = df_add_sum.sum(axis='columns')
        df_add_sum = self.sum_row(df_add_sum, self.sum_raw_name)
        return df_add_sum

    def maximum_likelihood_estimate(self) -> pd.DataFrame:
        """
        分割表の最尤推定値を計算したDataFrameを返す。

        Returns
        -------
        df_estimated: pd.DataFrame
            初期化引数df_cont_tbの最尤推定値を計算したDataFrame。
        """
        data_raw_sum = self.df_cont_tb.sum(axis='index')
        data_col_sum = self.df_cont_tb.sum(axis='columns')
        data_all_sum = data_raw_sum.sum()

        estimated_data = []
        for r_sum in data_col_sum:
            estimated_col = []
            for c_sum in data_raw_sum:
                estimated_col.append(r_sum * c_sum / data_all_sum ** 2)
            estimated_data.append(estimated_col)

        df_estimated = pd.DataFrame(estimated_data, self.df_cont_tb.index, self.df_cont_tb.columns)
        return df_estimated

    def get_expected_frequency(self) -> pd.DataFrame:
        """
        分割表の推定度数を計算したDataFrameを返す。

        Returns
        -------
        df_freq: pd.DataFrame
            初期化引数df_cont_tbの推定度数を計算したDataFrame。
        """
        data_raw_sum = self.df_cont_tb.sum(axis='index')
        data_col_sum = self.df_cont_tb.sum(axis='columns')
        data_all_sum = data_raw_sum.sum()

        freq_data = []
        for r_sum in data_col_sum:
            freq_col = []
            for c_sum in data_raw_sum:
                freq_col.append(r_sum * c_sum / data_all_sum)
            freq_data.append(freq_col)

        df_freq = pd.DataFrame(freq_data, self.df_cont_tb.index, self.df_cont_tb.columns)
        return df_freq

    def get_partial_fit(self):
        """
        Returns
        -------
        df_fit: pd.DataFrame
            分割表の項目ごとのカイ二乗適合度。
        """
        df_src = self.df_cont_tb.copy()
        df_est = self.get_expected_frequency()
        df_fit = (df_src - df_est) ** 2 / df_est
        return df_fit

    def chi2_fit_test(self, per_point: float) -> dict:
        """
        カイ二乗適合度検定を実行。
        分割表の行項目と列項目に対して独立性の帰無仮説を検証する。

        Parameters
        ----------
        per_point: float object
            カイ二乗分布の上側確率（実数）。

        Returns
        -------
        test_info: dict included in 'chi2_fit', 'chi2_per', 'test_result'
            'chi2_fit'は推定度数によるカイ二乗適合度の値。
            'chi2_per'は指定したカイ二乗分布の上側確率におけるパーセント点。
            'test_result'は帰無仮説が棄却される場合False、棄却されない場合True。
        """
        df_src = self.df_cont_tb.copy()
        df_est = self.get_expected_frequency()

        # カイ二乗適合度
        df_fit = (df_src - df_est) ** 2 / df_est
        chi2_fit = df_fit.sum(axis='columns').sum()

        # カイ二乗分布上側確率
        df = (len(self.df_cont_tb.index) - 1) * (len(self.df_cont_tb.columns) - 1)
        chi2_per = stats.chi2.ppf(q=per_point, df=df)

        # 検定
        test_result = False if chi2_fit > chi2_per else True

        test_info = {
            'chi2_fit': chi2_fit,
            'chi2_per': chi2_per,
            'test_result': test_result
        }
        return test_info

    def likelihood_ratio_test(self):
        pass

    @staticmethod
    def sum_row(df: pd.DataFrame, raw_name: str) -> pd.DataFrame:
        df_result = df.copy()
        df_row_sum = pd.DataFrame(df.sum(axis='index')).T
        df_row_sum.index = [raw_name]
        return df_result.append(df_row_sum)
