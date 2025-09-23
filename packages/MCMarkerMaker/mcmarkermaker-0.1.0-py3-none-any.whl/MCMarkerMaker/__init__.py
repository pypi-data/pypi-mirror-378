from typing import List, Optional

class Marker:
    """Internal class to represent a single Avid marker."""
    def __init__(self, tc: str, user: str, track: str, color: str, comment: str):
        
        self.tc = tc
        self.user = user
        self.track = track
        self.color = color
        self.comment = comment

    def format(self) -> str:
        """Formats the marker data into the Avid-compatible string format."""
    
        return f"{self.user}\t{self.tc}\t{self.track}\t{self.color}\t{self.comment}\t1\t\t{self.color}\n"

class AvidMarkerList:
    """
    A class to create and manage a list of Avid markers for export.
    
    This class provides a user-friendly way to build a marker list
    and write it to an Avid-compatible text file.
    """
    def __init__(self):
        self._markers: List[Marker] = []

    def add_marker(self, tc: str, comment: str = "", color: str = "Green", track: str = "V1", user: str = "User"):
        """
        Adds a new marker to the list.

        Args:
            tc (str): The timecode for the marker (e.g., "01:00:15:23"). This is the only
                      required argument.
            comment (str, optional): The text comment for the marker. Defaults to "".
            color (str, optional): The marker color. Defaults to "Green".
            track (str, optional): The track for the marker (e.g., "V1", "A2"). Defaults to "V1".
            user (str, optional): The user name associated with the marker. Defaults to "User".
        """
        marker = Marker(tc=tc, user=user, track=track, color=color, comment=comment)
        self._markers.append(marker)

    def export_to_file(self, output_path: str) -> tuple[bool, Optional[Exception]]:
        """
        Writes all added markers to a text file.

        Args:
            output_path (str): The full destination path for the output .txt file.

        Returns:
            tuple[bool, Optional[Exception]]: A tuple containing a success status (True/False)
                                             and an Exception object if an error occurred.
        """
        try:
            with open(output_path, 'w', encoding="utf-8") as f:
                for marker in self._markers:
                    f.write(marker.format())
            return True, None
        except Exception as e:
            return False, e