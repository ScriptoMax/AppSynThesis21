import React from 'react';

import './assets/css/bootstrap.min.css';
import './global.css';
import Routes from './routes';

class App extends React.Component {
    render() {
        return (
            <div>
                <Routes/>
            </div>
        );
    }
}

export default App;