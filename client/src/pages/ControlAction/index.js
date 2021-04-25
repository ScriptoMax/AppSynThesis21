import React from 'react';

import '../Base/style.css';
import api from "../../services/api";

class ControlAction extends React.Component {

    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
    }


    async handleInitRequest() {

        try {
            await api.post('session/init/', {
                user_id: localStorage.getItem('userId'),
                host_ip: '192.168.1.2'
            }, {
                headers: {
                    'Authorization': localStorage.getItem('userToken')
                }
            }).then(response => {
                let websocketAddress = 'ws://' + response.data['ws_address'] + '/sub'
                console.log('address: ' + websocketAddress)
                localStorage.setItem('websocketAddress', websocketAddress);
                localStorage.setItem('sessionStatus', 'active')
            }).catch(err => {
                console.log(err)
            });

            localStorage.setItem('sessionStatus', 'active')
            localStorage.setItem('partialTranscript', '')
            localStorage.setItem('fullTranscript', '')
        } catch(err) {
            alert('Session opening refused as request includes incomplete or wrong parameters')
        }
    }

    async handleCancelRequest() {

        try {
            await api.post('session/cancel/', {
                host_ip: '192.168.1.2'
            }, {
                headers: {
                    'Authorization': localStorage.getItem('userToken')
                }
            }).then(response => {
                let resultCode = response.status
                console.log('server response code: ' + resultCode)
            }).catch(err => {
                console.log(err)
            });
            localStorage.setItem('sessionStatus', 'close')
            localStorage.setItem('partialTranscript', '')
            localStorage.setItem('fullTranscript', '')
        } catch (err) {
            alert('Session closing refused as request includes incomplete or wrong parameters')
        }
    }
}

export default ControlAction