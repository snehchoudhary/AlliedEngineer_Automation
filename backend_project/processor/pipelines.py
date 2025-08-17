# from __future__ import annotations
# from dataclasses import dataclass
# from pathlib import Path
# import pandas as pd
# from .utils import read_table, write_excel, safe_columns


# @dataclass
# class ProcResult:
#     output_path: Path


# # ---------- 1) LAND USE ----------
# # Based on your Land_Use.py

# def process_land_use(in_file: Path) -> ProcResult:
#     df = read_table(in_file)
#     df.columns = df.columns.str.strip()

#     # Station handling
#     if "Station (m)" in df.columns:
#         df["End Station (m)"] = df["Station (m)"]
#     elif "Station m" in df.columns:
#         df.rename(columns={"Station m": "Station (m)"}, inplace=True)
#         df["End Station (m)"] = df["Station (m)"]
#     else:
#         df["Station (m)"] = None
#         df["End Station (m)"] = None

#     # Comments
#     df["Comment"] = df.get("Comment", pd.Series([None]*len(df))).fillna("").astype(str)
#     df["Normalized_Comment"] = df["Comment"].str.lower()

#     base_keywords = [
#         "road", "surface pavement", "gravel", "surfaced pavement", "gravel surface",
#         "surfaced - pavement", "surfaced-pavement", "surface-pavement", "rocky",
#         "cobble", "surface - pavement", "highway", "railroad tracks",
#     ]

#     results = []
#     start_row = None
#     start_index = None
#     current_keyword = None

#     for i, row in df.iterrows():
#         comment = row["Normalized_Comment"]
#         for keyword in base_keywords:
#             if f"{keyword} start" in comment:
#                 start_row = row
#                 start_index = i
#                 current_keyword = keyword
#                 break

#         if start_row is not None and current_keyword and f"{current_keyword} end" in comment:
#             end_row = row
#             end_index = i
#             attenuation_avg = df.loc[start_index:end_index, "Attenuation"].mean() if "Attenuation" in df.columns else None

#             result = start_row.to_dict()
#             result.update(
#                 {
#                     "End VirtualDistance (m)": end_row.get("VirtualDistance (m)", None),
#                     "End Station (m)": end_row.get("End Station (m)", None),
#                     "End Latitude": end_row.get("Latitude", None),
#                     "End Longitude": end_row.get("Longitude", None),
#                     "Average Attenuation": attenuation_avg,
#                 }
#             )
#             results.append(result)
#             start_row = None
#             current_keyword = None

#     output_df = pd.DataFrame(results)
#     if not output_df.empty:
#         output_df["Length (m)"] = output_df["End VirtualDistance (m)"] - output_df["VirtualDistance (m)"]

#     columns_to_keep = [
#         "SortIndex",
#         "VirtualDistance (m)",
#         "End VirtualDistance (m)",
#         "Length (m)",
#         "Station (m)",
#         "End Station (m)",
#         "Latitude",
#         "Longitude",
#         "End Latitude",
#         "End Longitude",
#         "DepthOfCover (m)",
#         "Normalized_Comment",
#         "Average Attenuation",
#     ]

#     output_df = safe_columns(output_df, columns_to_keep)[columns_to_keep]
#     out_path = in_file.with_name(f"{in_file.stem} Land_Use_Export.xlsx")
#     write_excel(output_df, out_path)
#     return ProcResult(out_path)


# # ---------- 2) CIPS On PSP (< threshold) ----------
# # Based on your CIPS On PSP.py, cleaned + fixed

# def process_cips_on_psp(in_file: Path, threshold: float = -1.0) -> ProcResult:
#     df = read_table(in_file)
#     df.columns = df.columns.str.strip()

#     # Mirrors original expectations
#     if "Station m" in df.columns:
#         df["End Station (m)"] = df["Station m"]

#     df["End VirtualDistance (m)"] = df["VirtualDistance (m)"]
#     df["End Latitude"] = df["Latitude"]
#     df["End Longitude"] = df["Longitude"]

#     # Select rows where CPCIPS_OnPotential < threshold, club consecutive runs
#     if "CPCIPS_OnPotential" not in df.columns:
#         raise ValueError("Column 'CPCIPS_OnPotential' not found")

#     df["Above_Threshold"] = df["CPCIPS_OnPotential"] < float(threshold)

#     def process_group(group: pd.DataFrame) -> pd.DataFrame:
#         if group["Above_Threshold"].any():
#             min_value = group["CPCIPS_OnPotential"].min()
#             group["Lowest CPCIPS OnPotential"] = min_value
#             chainage = group.loc[group["CPCIPS_OnPotential"] == min_value, "VirtualDistance (m)"].values[0]
#             group["Chainage of Lowest Reading"] = chainage

#             avg_value = group["CPCIPS_OnPotential"].mean()
#             group["Average CPCIPS OnPotential"] = avg_value
#             chainage_avg = group.loc[(group["CPCIPS_OnPotential"] - avg_value).abs().idxmin(), "VirtualDistance (m)"] if len(group) else None
#             group["Chainage of Average Reading"] = chainage_avg

#             if len(group) > 1:
#                 if "End Station (m)" in group.columns:
#                     group.iloc[0, group.columns.get_loc("End Station (m)")] = group.iloc[-1]["End Station (m)"]
#                 group.iloc[0, group.columns.get_loc("End Latitude")] = group.iloc[-1]["End Latitude"]
#                 group.iloc[0, group.columns.get_loc("End Longitude")] = group.iloc[-1]["End Longitude"]
#                 group.iloc[0, group.columns.get_loc("End VirtualDistance (m)")] = group.iloc[-1]["End VirtualDistance (m)"]
#         return group

#     df = df.groupby((df["Above_Threshold"] != df["Above_Threshold"].shift()).cumsum(), group_keys=False).apply(process_group)
#     df = df[df["Above_Threshold"]].loc[df["Above_Threshold"] != df["Above_Threshold"].shift()]
#     df = df.drop(columns=["Above_Threshold"]) if "Above_Threshold" in df.columns else df

#     df["Length (m)"] = df["End VirtualDistance (m)"] - df["VirtualDistance (m)"]

#     columns_to_keep = [
#         "SortIndex",
#         "VirtualDistance (m)",
#         "End VirtualDistance (m)",
#         "Length (m)",
#         "Station (m)",
#         "End Station (m)",
#         "Latitude",
#         "Longitude",
#         "End Latitude",
#         "End Longitude",
#         "DepthOfCover (m)",
#         "CPCIPS_OnPotential",
#         "Lowest CPCIPS OnPotential",
#         "Chainage of Lowest Reading",
#         "Average CPCIPS OnPotential",
#         "Chainage of Average Reading",
#     ]

#     output_df = safe_columns(df, columns_to_keep)[columns_to_keep]
#     out_path = in_file.with_name(f"{in_file.stem} CIPS_On_PSP_Export.xlsx")
#     write_excel(output_df, out_path)
#     return ProcResult(out_path)


# # ---------- 3) Attenuation ACCA ----------
# def process_attenuation_acca(in_file: Path, threshold: float = 2.0) -> ProcResult:
#     df = read_table(in_file)
#     df.columns = df.columns.str.strip()

#     if "Attenuation" not in df.columns:
#         raise ValueError("Column 'Attenuation' not found")

#     df["Above_Threshold"] = df["Attenuation"] >= float(threshold)

#     def process_group(group: pd.DataFrame) -> pd.DataFrame:
#         if group["Above_Threshold"].any():
#             max_value = group["Attenuation"].max()
#             group["Highest Attenuation"] = max_value
#             chainage = group.loc[group["Attenuation"] == max_value, "VirtualDistance (m)"].values[0]
#             group["Chainage of Highest Reading"] = chainage

#             avg_value = group["Attenuation"].mean()
#             group["Average Attenuation"] = avg_value
#             chainage_avg = group.loc[(group["Attenuation"] - avg_value).abs().idxmin(), "VirtualDistance (m)"] if len(group) else None
#             group["Chainage of Average Reading"] = chainage_avg

#             if len(group) > 1:
#                 if "End Station (m)" in group.columns:
#                     group.iloc[0, group.columns.get_loc("End Station (m)")] = group.iloc[-1]["End Station (m)"]
#                 group.iloc[0, group.columns.get_loc("End Latitude")] = group.iloc[-1]["End Latitude"]
#                 group.iloc[0, group.columns.get_loc("End Longitude")] = group.iloc[-1]["End Longitude"]
#                 group.iloc[0, group.columns.get_loc("End VirtualDistance (m)")] = group.iloc[-1]["End VirtualDistance (m)"]
#         return group

#     df = df.groupby((df["Above_Threshold"] != df["Above_Threshold"].shift()).cumsum(), group_keys=False).apply(process_group)
#     df = df[df["Above_Threshold"]].loc[df["Above_Threshold"] != df["Above_Threshold"].shift()]
#     df = df.drop(columns=["Above_Threshold"]) if "Above_Threshold" in df.columns else df

#     df["Length (m)"] = df["End VirtualDistance (m)"] - df["VirtualDistance (m)"]

#     columns_to_keep = [
#         "SortIndex",
#         "VirtualDistance (m)",
#         "End VirtualDistance (m)",
#         "Length (m)",
#         "Station (m)",
#         "End Station (m)",
#         "Latitude",
#         "Longitude",
#         "End Latitude",
#         "End Longitude",
#         "DepthOfCover (m)",
#         "Attenuation",
#         "Highest Attenuation",
#         "Chainage of Highest Reading",
#         "Average Attenuation",
#         "Chainage of Average Reading",
#     ]

#     output_df = safe_columns(df, columns_to_keep)[columns_to_keep]
#     out_path = in_file.with_name(f"{in_file.stem} Attenuation_ACCA_Export.xlsx")
#     write_excel(output_df, out_path)
#     return ProcResult(out_path)


# # ---------- 4) AC PSP ----------
# def process_ac_psp(in_file: Path, threshold: float = 4.0) -> ProcResult:
#     df = read_table(in_file)
#     df.columns = df.columns.str.strip()

#     if "AC_PSP" not in df.columns:
#         raise ValueError("Column 'AC_PSP' not found")

#     df["Above_Threshold"] = df["AC_PSP"] >= float(threshold)

#     def process_group(group: pd.DataFrame) -> pd.DataFrame:
#         if group["Above_Threshold"].any():
#             max_value = group["AC_PSP"].max()
#             group["Highest AC PSP"] = max_value
#             chainage = group.loc[group["AC_PSP"] == max_value, "VirtualDistance (m)"].values[0]
#             group["Chainage of Highest Reading"] = chainage

#             avg_value = group["AC_PSP"].mean()
#             group["Average AC PSP"] = avg_value
#             chainage_avg = group.loc[(group["AC_PSP"] - avg_value).abs().idxmin(), "VirtualDistance (m)"] if len(group) else None
#             group["Chainage of Average Reading"] = chainage_avg

#             if len(group) > 1:
#                 if "End Station (m)" in group.columns:
#                     group.iloc[0, group.columns.get_loc("End Station (m)")] = group.iloc[-1]["End Station (m)"]
#                 group.iloc[0, group.columns.get_loc("End Latitude")] = group.iloc[-1]["End Latitude"]
#                 group.iloc[0, group.columns.get_loc("End Longitude")] = group.iloc[-1]["End Longitude"]
#                 group.iloc[0, group.columns.get_loc("End VirtualDistance (m)")] = group.iloc[-1]["End VirtualDistance (m)"]
#         return group

#     df = df.groupby((df["Above_Threshold"] != df["Above_Threshold"].shift()).cumsum(), group_keys=False).apply(process_group)
#     df = df[df["Above_Threshold"]].loc[df["Above_Threshold"] != df["Above_Threshold"].shift()]
#     df = df.drop(columns=["Above_Threshold"]) if "Above_Threshold" in df.columns else df

#     df["Length (m)"] = df["End VirtualDistance (m)"] - df["VirtualDistance (m)"]

#     columns_to_keep = [
#         "SortIndex",
#         "VirtualDistance (m)",
#         "End VirtualDistance (m)",
#         "Length (m)",
#         "Station (m)",
#         "End Station (m)",
#         "Latitude",
#         "Longitude",
#         "End Latitude",
#         "End Longitude",
#         "DepthOfCover (m)",
#         "AC_PSP",
#         "Highest AC PSP",
#         "Chainage of Highest Reading",
#         "Average AC PSP",
#         "Chainage of Average Reading",
#     ]

#     output_df = safe_columns(df, columns_to_keep)[columns_to_keep]
#     out_path = in_file.with_name(f"{in_file.stem} AC_PSP_Export.xlsx")
#     write_excel(output_df, out_path)
#     return ProcResult(out_path)


# # ---------- PROCESSOR MAP ----------
# PROCESSOR_MAP = {
#     "land_use": process_land_use,
#     "cips_on_psp": process_cips_on_psp,
#     "attenuation_acca": process_attenuation_acca,
#     "ac_psp": process_ac_psp,
# }


from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from .utils import read_table, write_excel, safe_columns


@dataclass
class ProcResult:
    output_path: Path


# ---------- 1) LAND USE ----------
def process_land_use(in_file: Path) -> ProcResult:
    df = read_table(in_file)
    df.columns = df.columns.str.strip()

    # Station handling
    if "Station (m)" in df.columns:
        df["End Station (m)"] = df["Station (m)"]
    elif "Station m" in df.columns:
        df.rename(columns={"Station m": "Station (m)"}, inplace=True)
        df["End Station (m)"] = df["Station (m)"]
    else:
        df["Station (m)"] = None
        df["End Station (m)"] = None

    # Comments
    df["Comment"] = df.get("Comment", pd.Series([None]*len(df))).fillna("").astype(str)
    df["Normalized_Comment"] = df["Comment"].str.lower()

    base_keywords = [
        "road", "surface pavement", "gravel", "surfaced pavement", "gravel surface",
        "surfaced - pavement", "surfaced-pavement", "surface-pavement", "rocky",
        "cobble", "surface - pavement", "highway", "railroad tracks",
    ]

    results = []
    start_row = None
    start_index = None
    current_keyword = None

    for i, row in df.iterrows():
        comment = row["Normalized_Comment"]
        for keyword in base_keywords:
            if f"{keyword} start" in comment:
                start_row = row
                start_index = i
                current_keyword = keyword
                break

        if start_row is not None and current_keyword and f"{current_keyword} end" in comment:
            end_row = row
            end_index = i
            attenuation_avg = df.loc[start_index:end_index, "Attenuation"].mean() if "Attenuation" in df.columns else None

            result = start_row.to_dict()
            result.update(
                {
                    "End VirtualDistance (m)": end_row.get("VirtualDistance (m)", None),
                    "End Station (m)": end_row.get("End Station (m)", None),
                    "End Latitude": end_row.get("Latitude", None),
                    "End Longitude": end_row.get("Longitude", None),
                    "Average Attenuation": attenuation_avg,
                }
            )
            results.append(result)
            start_row = None
            current_keyword = None

    output_df = pd.DataFrame(results)
    if not output_df.empty:
        output_df["Length (m)"] = output_df["End VirtualDistance (m)"] - output_df["VirtualDistance (m)"]

    columns_to_keep = [
        "SortIndex",
        "VirtualDistance (m)",
        "End VirtualDistance (m)",
        "Length (m)",
        "Station (m)",
        "End Station (m)",
        "Latitude",
        "Longitude",
        "End Latitude",
        "End Longitude",
        "DepthOfCover (m)",
        "Normalized_Comment",
        "Average Attenuation",
    ]

    output_df = safe_columns(output_df, columns_to_keep)[columns_to_keep]
    out_path = in_file.with_name(f"{in_file.stem} Land_Use_Export.xlsx")
    write_excel(output_df, out_path)
    return ProcResult(out_path)


# ---------- 2) CIPS On PSP ----------
def process_cips_on_psp(in_file: Path, threshold: float = -1.0) -> ProcResult:
    df = read_table(in_file)
    df.columns = df.columns.str.strip()

    if "Station m" in df.columns:
        df["End Station (m)"] = df["Station m"]

    df["End VirtualDistance (m)"] = df["VirtualDistance (m)"]
    df["End Latitude"] = df["Latitude"]
    df["End Longitude"] = df["Longitude"]

    if "CPCIPS_OnPotential" not in df.columns:
        raise ValueError("Column 'CPCIPS_OnPotential' not found")

    df["Above_Threshold"] = df["CPCIPS_OnPotential"] < float(threshold)

    def process_group(group: pd.DataFrame) -> pd.DataFrame:
        if group["Above_Threshold"].any():
            min_value = group["CPCIPS_OnPotential"].min()
            group["Lowest CPCIPS OnPotential"] = min_value
            chainage = group.loc[group["CPCIPS_OnPotential"] == min_value, "VirtualDistance (m)"].values[0]
            group["Chainage of Lowest Reading"] = chainage

            avg_value = group["CPCIPS_OnPotential"].mean()
            group["Average CPCIPS OnPotential"] = avg_value
            chainage_avg = group.loc[(group["CPCIPS_OnPotential"] - avg_value).abs().idxmin(), "VirtualDistance (m)"] if len(group) else None
            group["Chainage of Average Reading"] = chainage_avg

            if len(group) > 1:
                if "End Station (m)" in group.columns:
                    group.iloc[0, group.columns.get_loc("End Station (m)")] = group.iloc[-1]["End Station (m)"]
                group.iloc[0, group.columns.get_loc("End Latitude")] = group.iloc[-1]["End Latitude"]
                group.iloc[0, group.columns.get_loc("End Longitude")] = group.iloc[-1]["End Longitude"]
                group.iloc[0, group.columns.get_loc("End VirtualDistance (m)")] = group.iloc[-1]["End VirtualDistance (m)"]
        return group

    df = df.groupby((df["Above_Threshold"] != df["Above_Threshold"].shift()).cumsum(), group_keys=False).apply(process_group)
    df = df[df["Above_Threshold"]].loc[df["Above_Threshold"] != df["Above_Threshold"].shift()]
    df = df.drop(columns=["Above_Threshold"]) if "Above_Threshold" in df.columns else df

    df["Length (m)"] = df["End VirtualDistance (m)"] - df["VirtualDistance (m)"]

    columns_to_keep = [
        "SortIndex", "VirtualDistance (m)", "End VirtualDistance (m)", "Length (m)",
        "Station (m)", "End Station (m)", "Latitude", "Longitude", "End Latitude", "End Longitude",
        "DepthOfCover (m)", "CPCIPS_OnPotential", "Lowest CPCIPS OnPotential",
        "Chainage of Lowest Reading", "Average CPCIPS OnPotential", "Chainage of Average Reading",
    ]

    output_df = safe_columns(df, columns_to_keep)[columns_to_keep]
    out_path = in_file.with_name(f"{in_file.stem} CIPS_On_PSP_Export.xlsx")
    write_excel(output_df, out_path)
    return ProcResult(out_path)


# ---------- 3) Attenuation ACCA ----------
def process_attenuation_acca(in_file: Path, threshold: float = 2.0) -> ProcResult:
    df = read_table(in_file)
    df.columns = df.columns.str.strip()

    if "Attenuation" not in df.columns:
        raise ValueError("Column 'Attenuation' not found")

    df["Above_Threshold"] = df["Attenuation"] >= float(threshold)

    def process_group(group: pd.DataFrame) -> pd.DataFrame:
        if group["Above_Threshold"].any():
            max_value = group["Attenuation"].max()
            group["Highest Attenuation"] = max_value
            chainage = group.loc[group["Attenuation"] == max_value, "VirtualDistance (m)"].values[0]
            group["Chainage of Highest Reading"] = chainage

            avg_value = group["Attenuation"].mean()
            group["Average Attenuation"] = avg_value
            chainage_avg = group.loc[(group["Attenuation"] - avg_value).abs().idxmin(), "VirtualDistance (m)"] if len(group) else None
            group["Chainage of Average Reading"] = chainage_avg

            if len(group) > 1:
                if "End Station (m)" in group.columns:
                    group.iloc[0, group.columns.get_loc("End Station (m)")] = group.iloc[-1]["End Station (m)"]
                group.iloc[0, group.columns.get_loc("End Latitude")] = group.iloc[-1]["End Latitude"]
                group.iloc[0, group.columns.get_loc("End Longitude")] = group.iloc[-1]["End Longitude"]
                group.iloc[0, group.columns.get_loc("End VirtualDistance (m)")] = group.iloc[-1]["End VirtualDistance (m)"]
        return group

    df = df.groupby((df["Above_Threshold"] != df["Above_Threshold"].shift()).cumsum(), group_keys=False).apply(process_group)
    df = df[df["Above_Threshold"]].loc[df["Above_Threshold"] != df["Above_Threshold"].shift()]
    df = df.drop(columns=["Above_Threshold"]) if "Above_Threshold" in df.columns else df

    df["Length (m)"] = df["End VirtualDistance (m)"] - df["VirtualDistance (m)"]

    columns_to_keep = [
        "SortIndex", "VirtualDistance (m)", "End VirtualDistance (m)", "Length (m)",
        "Station (m)", "End Station (m)", "Latitude", "Longitude", "End Latitude", "End Longitude",
        "DepthOfCover (m)", "Attenuation", "Highest Attenuation", "Chainage of Highest Reading",
        "Average Attenuation", "Chainage of Average Reading",
    ]

    output_df = safe_columns(df, columns_to_keep)[columns_to_keep]
    out_path = in_file.with_name(f"{in_file.stem} Attenuation_ACCA_Export.xlsx")
    write_excel(output_df, out_path)
    return ProcResult(out_path)


# ---------- 4) AC PSP ----------
def process_ac_psp(in_file: Path, threshold: float = 4.0) -> ProcResult:
    df = read_table(in_file)
    df.columns = df.columns.str.strip()

    if "AC_PSP" not in df.columns:
        raise ValueError("Column 'AC_PSP' not found")

    df["Above_Threshold"] = df["AC_PSP"] >= float(threshold)

    def process_group(group: pd.DataFrame) -> pd.DataFrame:
        if group["Above_Threshold"].any():
            max_value = group["AC_PSP"].max()
            group["Highest AC PSP"] = max_value
            chainage = group.loc[group["AC_PSP"] == max_value, "VirtualDistance (m)"].values[0]
            group["Chainage of Highest Reading"] = chainage

            avg_value = group["AC_PSP"].mean()
            group["Average AC PSP"] = avg_value
            chainage_avg = group.loc[(group["AC_PSP"] - avg_value).abs().idxmin(), "VirtualDistance (m)"] if len(group) else None
            group["Chainage of Average Reading"] = chainage_avg

            if len(group) > 1:
                if "End Station (m)" in group.columns:
                    group.iloc[0, group.columns.get_loc("End Station (m)")] = group.iloc[-1]["End Station (m)"]
                group.iloc[0, group.columns.get_loc("End Latitude")] = group.iloc[-1]["End Latitude"]
                group.iloc[0, group.columns.get_loc("End Longitude")] = group.iloc[-1]["End Longitude"]
                group.iloc[0, group.columns.get_loc("End VirtualDistance (m)")] = group.iloc[-1]["End VirtualDistance (m)"]
        return group

    df = df.groupby((df["Above_Threshold"] != df["Above_Threshold"].shift()).cumsum(), group_keys=False).apply(process_group)
    df = df[df["Above_Threshold"]].loc[df["Above_Threshold"] != df["Above_Threshold"].shift()]
    df = df.drop(columns=["Above_Threshold"]) if "Above_Threshold" in df.columns else df

    df["Length (m)"] = df["End VirtualDistance (m)"] - df["VirtualDistance (m)"]

    columns_to_keep = [
        "SortIndex", "VirtualDistance (m)", "End VirtualDistance (m)", "Length (m)",
        "Station (m)", "End Station (m)", "Latitude", "Longitude", "End Latitude", "End Longitude",
        "DepthOfCover (m)", "AC_PSP", "Highest AC PSP", "Chainage of Highest Reading",
        "Average AC PSP", "Chainage of Average Reading",
    ]

    output_df = safe_columns(df, columns_to_keep)[columns_to_keep]
    out_path = in_file.with_name(f"{in_file.stem} AC_PSP_Export.xlsx")
    write_excel(output_df, out_path)
    return ProcResult(out_path)


# ---------- 5) AC Interference ----------
def process_ac_interference(in_file: Path) -> ProcResult:
    df = read_table(in_file)
    df.columns = df.columns.str.strip()

    # Normalize for safer matching
    normalized_cols = {c.lower().replace(" ", "_"): c for c in df.columns}
    print("🔎 Available columns:", normalized_cols)  # debugging

    # Map actual column
    target_col = None
    for key in normalized_cols:
        if key in ["ac_interference", "acvg_vss_db"]:  # accept both
            target_col = normalized_cols[key]
            break

    if not target_col:
        raise ValueError(f"Expected 'AC_Interference' or 'ACVG_VSS_DB' column, found {list(df.columns)}")

    # Example logic: keep only rows where interference > 0
    df = df[df[target_col] > 0]

    out_path = in_file.with_name(f"{in_file.stem} AC_Interference_Export.xlsx")
    write_excel(df, out_path)
    return ProcResult(out_path)



# ---------- PROCESSOR MAP ----------
PROCESSOR_MAP = {
    "land_use": process_land_use,
    "cips_on_psp": process_cips_on_psp,
    "attenuation_acca": process_attenuation_acca,
    "ac_psp": process_ac_psp,
    "ac_interference": process_ac_interference,
}
