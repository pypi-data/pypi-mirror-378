# MCMarkerMaker

A simple utility to create text files for importing sequence markers into Avid Media Composer.

## Installation

Install the package using pip:

```bash
pip install MCMarkerMaker
```

## Usage

Here's a quick example of how to create a marker file:

```python
from MCMarkerMaker import AvidMarkerList

# 1. Create an instance of the marker list manager
my_markers = AvidMarkerList()

# 2. Add markers one-by-one
my_markers.add_marker(tc="01:00:10:05", comment="Start of interview")
my_markers.add_marker(tc="01:02:30:00", comment="Key moment", color="Red")

# 3. Export the list to a file
output_file = "project_markers.txt"
success, error = my_markers.export_to_file(output_file)

if success:
    print(f"Marker file created at: {output_file}")
else:
    print(f"An error occurred: {error}")
```