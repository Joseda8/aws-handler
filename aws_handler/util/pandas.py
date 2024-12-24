import io

import pandas as pd


@staticmethod
def format_df_to_excel(df_data: pd.DataFrame) -> io.BytesIO:
    """
    Formats a Pandas DataFrame to an Excel buffer with headers
    filtering and column adjustments.

    :param df_data: Pandas DataFrame to format.
    :return: Excel buffer containing the formatted DataFrame.
    """
    excel_buffer = io.BytesIO()
    # Use the XlsxWriter engine to write the DataFrame to the buffer
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_data.to_excel(writer, index=False, sheet_name="data")
        worksheet = writer.sheets["data"]
        # Add filters to the headers
        worksheet.autofilter(0, 0, df_data.shape[0], df_data.shape[1] - 1)
        # Adjust column width to fit content and headers
        for i, col in enumerate(df_data.columns):
            max_length = (
                max(
                    # Length of the longest cell in the column
                    df_data[col].astype(str).map(len).max(),
                    # Length of the column header
                    len(str(col)),
                )
                + 2
            )
            worksheet.set_column(i, i, max_length)

    excel_buffer.seek(0)
    return excel_buffer
