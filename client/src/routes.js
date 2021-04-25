import React from 'react';
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ExpressReport from './pages/ExpressReport';
import ViewTicket from './pages/ViewTicket';

export default function Routes() {
    return (
        <Router>
            <Switch>
                <Route path="/" exact component={Login}/>
                <Route path="/register"  component={Register}/>
                <Route path="/dashboard" component={Dashboard}/>
                <Route path="/expressReport" component={ExpressReport}/>
                <Route path="/viewticket" component={ViewTicket}/>
            </Switch>
        </Router>
    );
}