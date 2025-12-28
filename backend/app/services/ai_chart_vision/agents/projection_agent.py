class ProjectionAgent:
    def __init__(self):
        pass

    def project_htf_to_ltf(self, htf_zone, ltf_dataframe):
        """
        Takes a zone (e.g., Weekly FVG) and finds the exact start/end indices
        on the 4H chart.
        """
        if not htf_zone or ltf_dataframe.empty:
            return None

        # Convert zone times to pandas compatible format if not already
        start_time = htf_zone.get('start_time')
        end_time = htf_zone.get('end_time')

        # Filter LTF candles that fall within the HTF timestamp range
        mask = (ltf_dataframe.index >= start_time) & (ltf_dataframe.index <= end_time)
        ltf_indices = ltf_dataframe.index[mask]

        if len(ltf_indices) == 0:
            return None

        # We return the integer location (index) for plotting on the x-axis
        start_idx = ltf_dataframe.index.get_loc(ltf_indices[0])
        end_idx = ltf_dataframe.index.get_loc(ltf_indices[-1])
        
        # Handle slice vs single integer return
        if isinstance(start_idx, slice): start_idx = start_idx.start
        if isinstance(end_idx, slice): end_idx = end_idx.stop - 1

        return {
            "start_x_index": int(start_idx),
            "end_x_index": int(end_idx),
            "price_top": htf_zone.get('top'),
            "price_bottom": htf_zone.get('bottom'),
            "source_tf": htf_zone.get('tf', 'HTF') # e.g., 'WEEKLY'
        }
