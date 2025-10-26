# Frontend - React Visualization

Web-based visualization for the Distributed Internet Topology Mapper.

## Features

- Interactive network graph using vis.js
- Real-time topology updates
- Node statistics display
- GEXF file import/export
- Responsive design

## Setup

```bash
npm install
```

## Development

```bash
npm start
```

Opens at http://localhost:3000

## Build

```bash
npm run build
```

Creates optimized production build in `build/` directory.

## TODO

- [ ] Implement GEXF file parsing
- [ ] Add IPFS integration for loading topology data
- [ ] Implement export functionality
- [ ] Add filtering/search capabilities
- [ ] Show node details on click
- [ ] Add graph layout algorithms
- [ ] Implement real-time updates via WebSocket or IPFS PubSub
