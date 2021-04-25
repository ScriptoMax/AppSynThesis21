import React, {useState} from 'react';
import {useHistory} from 'react-router-dom';

import api from '../../services/api';

import './style.css';

export default function Register() {
    
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');

    const history = useHistory();

    async function hundleSubmit(e){

        e.preventDefault();

        try {

            const response = await api.post('/user', {
                name,
                password
            });

            localStorage.setItem('user_id', response.data.id);
            localStorage.setItem('user_name', name);
            localStorage.setItem('user_token', response.data.token);
            history.push('/dashboard');
        } catch(err) {
            console.log({"erro": err.response.data.error})
        }
    }

    return (
        <div className="container container-register">
            <section className="form-register">
                <form onSubmit={hundleSubmit}>
                    <input type="text" 
                        className="input" 
                        placeholder="Internal user name"
                        onChange={e => { setName(e.target.value)}} />
                    <input type="password"
                        className="input" 
                        placeholder="Password"
                        onChange={e => {setPassword(e.target.value)}} />
                    <button type="submit" className="button">Sign in</button>
                </form>
            </section>
        </div>
    );
}