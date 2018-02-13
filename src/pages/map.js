import React from 'react'
import ReactMapGL from 'react-map-gl'
import css from './map.sass'
import queryString from 'query-string'

class Map extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        latitude: this.props.lat,
        longitude: this.props.lon,
        zoom: this.props.zoom
      }
    }
  }

  componentDidMount() {
    window.addEventListener('resize', this._resize);
    this._resize();
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this._resize);
  }

  _onViewportChange = viewport => this.setState({
    viewport: {...this.state.viewport, ...viewport}
  });

  _resize = () => this._onViewportChange({
    width: this.props.width || window.innerWidth,
    height: this.props.height || window.innerHeight
  });

  render() {
    const {viewport, settings} = this.state
    return <ReactMapGL
      {...viewport}
      {...settings}
      id="map"
      mapStyle="mapbox://styles/mapbox/satellite-streets-v9"
      onViewportChange={this._onViewportChange}
    />
  }
}

const MapPage = ({ data }) => {
  const parsedHash = queryString.parse(location.search);
  const cityId = parsedHash.id
  const cityEdge = data.allCitiesJson.edges.find(e => e.node.internalId === cityId)
    || data.allCitiesJson.edges[0]
  const city = cityEdge.node
  console.log(city)

  return <Map
    zoom={city.zoom}
    lat={city.center.lat}
    lon={city.center.lon}
  />
}

export const query = graphql`
  query MapQuery {
    allCitiesJson {
      edges {
        node {
          internalId
          name
          country
          path
          center {
            lat
            lon
          }
          zoom
        }
      }
    }
  }
`

export default MapPage