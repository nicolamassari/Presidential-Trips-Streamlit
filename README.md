# France Presidential Travels Visualization

This project is a Streamlit web application that visualizes travel data of French Presidents and Prime Ministers from 1945 to 2008. Users can explore the locations visited, frequency of trips, and patterns over the years applying a variety of filters.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Data Source](#data-source)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Interactive Map**: Visualize countries visited by French leaders.
- **Top Locations**: Display the most visited locations.
- **Trip Frequency**: Show the number of trips per month and year.
- **Filters**: Filter data by function (President or Prime Minister), election years, and trips outside France.

## Technologies Used

- **Python**: The programming language used for development.
- **Streamlit**: A framework for building web applications quickly.
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical operations.
- **Matplotlib**: For data visualization.
- **Seaborn**: For enhanced data visualization.
- **GeoPandas**: For geographic data handling.
- **Altair**: For declarative statistical visualization.

## Installation

To run this project locally, you'll need to have Docker installed. Then, follow these steps:

1. **Clone the repository**:

   `git clone https://github.com/nicolamassari/Presidential-Trips-Streamlit.git`
   
   `cd Presidential-Trips-Streamlit`

2. **Build the Docker image**:

   `docker build -t presidential-travels-app .`

3. **Run the Docker container**:

   `docker run -p 8501:8501 presidential-travels-app`

4. **Open your web browser and go to** `http://localhost:8501`.

## Usage

- Use the checkboxes to filter trips outside France or to include only trips during election years.
- Select a President or Prime Minister to filter the data.
- Adjust the year range using the sliders to refine your results.
- Explore the interactive maps and charts to visualize the data.

## Data Source

The dataset used in this project is a JSON file containing records of presidential travels. The source is:

- **File**: `deplacements-presidents-republique-et-premiers-ministres-depuis-1945.json`
- **Description**: Contains information about trips made by French leaders, including dates, locations, and other relevant details.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your improvements or fixes.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
