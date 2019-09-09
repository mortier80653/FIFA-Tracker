import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import { renderToStaticMarkup } from "react-dom/server";
import { withLocalize, Translate } from "react-localize-redux";
import { BrowserRouter as Router, Route, Link as RouterLink } from "react-router-dom";
import { withStyles } from '@material-ui/styles';
import moment from 'moment';
import api_endpoints from '../../utils/endpoints.js';
import { check_refresh_token } from '../../utils/jwt_manager.js';
import axiosInstance from '../../utils/axiosInstance.js';
import defaultTrans from '../../translations/en.json';

import {
  Popover,
  IconButton,
  Icon,
  AppBar,
  Link,
  Toolbar,
  Tooltip,
  Grid,
  Typography,
  Button,
} from '@material-ui/core';

import { makeStyles } from '@material-ui/core/styles';


import TopBar from '../topbar/TopBar.js';
import Home from '../home/Home.js';
import Players from '../players/Players.js';
import MyCareers from '../mycareers/MyCareers.js';
import ActivateAccount from '../activateaccount/ActivateAccount.js';
import ResetPassword from '../resetpassword/ResetPassword.js';
import Footer from '../footer/Footer.js';

const styles = {
  main_container: {
    minHeight: "100vh",
    overflow: "hidden",
    display: "block",
    position: "relative",
    paddingBottom: "400px",
    '@media screen and (max-width: 769px)': {
      paddingBottom: "630px",
    }
  },
};

class Main extends React.Component {
    constructor(props) {
        super(props);

        let default_lang = localStorage.getItem('lang');
        if (default_lang == null) {
          localStorage.setItem('lang', 'en');
        }

        let localize_options = {
            renderToStaticMarkup: renderToStaticMarkup,
            renderInnerHtml: false,
        }

        // Prevent displaying "missing translation" on prod
        if (process.env.NODE_ENV !== 'development') {
          localize_options.onMissingTranslation = ({ defaultTranslation }) => defaultTranslation;
        }

        this.props.initialize({
          languages: [
            { name: "_", code: "_"},  // If It's Stupid But It Works...
            { name: "English", code: "en" },
            { name: "Polish", code: "pl" }
          ],
          options: localize_options
        });

        let is_logged_in = false;
        let username = (localStorage.getItem('username') || "guest");

        if ( (localStorage.getItem('username') !== null) && (check_refresh_token()) ) {
          is_logged_in = true;
          username = localStorage.getItem('username');
        }

        this.state = {
          user: {
            username: username,
          },
          isLoggedIn: is_logged_in,
        }

        this.handleRegister = this.handleRegister.bind(this);
        this.handleLogin = this.handleLogin.bind(this);
        this.handleLogout = this.handleLogout.bind(this);
    }

    componentDidMount() {
      let default_lang = localStorage.getItem('lang');
      import(`../../translations/${default_lang}.json`)
      .then( translations => {
        this.props.addTranslationForLanguage(translations, default_lang);
      });
      this.props.setActiveLanguage(default_lang);
    }

    clearLocalStorage(e) {
      localStorage.clear();
    }

  handleLogin(e, data) {
    e.preventDefault();
    axiosInstance(api_endpoints.login, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(data)
    })
    .then(res => {
        if (res.status === 200) {
          return res.data;
        }
      }
    )
    .then((json) => {
      const username = data.username;

      localStorage.setItem('token', json.access);
      localStorage.setItem('token_refresh', json.refresh);
      localStorage.setItem('token_refresh_expire', moment().add(5, 'd'));
      localStorage.setItem('username', username);
      this.setState({
        isLoggedIn: true,
        user: {
          username: username,
        },
      });
    })
    .catch((error) => {
      if (!error.response) {
        return
      }
      const err_code = error.response.data.code
      alert(error.response.data.detail)
    });
  }

  handleLogout(e) {
    localStorage.removeItem('token');
    localStorage.removeItem('token_refresh');
    localStorage.removeItem('token_expire');
    localStorage.removeItem('token_refresh_expire');
    localStorage.removeItem('username');

    this.setState({
      isLoggedIn: false,
    });
  }

  handleRegister(e, data) {
    e.preventDefault();

    if (data.password !== data.confirm_password) {
      alert(
        <Translate id="passwords_not_the_same">Your password and confirm password does not match</Translate>
      );
      return;
    };

    axiosInstance(api_endpoints.register, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(data)
    })
    .then(res => {
        if (res.status == 201) {
          return res.json();
        } else {
          throw res;
        }
      }
    )
    .then((json) => {
      alert(`Activation link has been sent to: ${json.email}`)
    })
    .catch((error) => {
      error.json().then((e) => {
        let err = "Error:\n";
        Object.keys(e).forEach((k) => {
          let o_k = `${k} - `;
          if (Array.isArray(e[k])) {
            o_k = o_k.concat(e[k].join('\n'));
          } else {
            o_k = o_k.concat(e[k]);
          };
          err = err.concat(`${o_k}\n`);
        });
        alert(err);
      })
    });
  }

    render() {
      const { classes } = this.props;
      const { user, isLoggedIn } = this.state;
      return (
        <div className={classes.main_container}>
          <Router>
            <TopBar
              handleLogin={this.handleLogin}
              handleRegister={this.handleRegister}
              handleLogout={this.handleLogout}
              isLoggedIn={isLoggedIn}
              user={user}
            />
            <Route path="/" exact component={Home} />
            <Route path="/players/" component={Players} />
            <Route
              path="/my-careers/"
              render={(props) => <MyCareers {...props} handleLogout={ this.handleLogout } isLoggedIn={ isLoggedIn }  />}
            />
            <Route
              path="/activate/:uidb64/:token/"
              render={(props) => <ActivateAccount {...props} isLoggedIn={ isLoggedIn } />}
            />
            <Route
              path="/reset-password/:uidb64/:token/"
              render={(props) => <ResetPassword {...props} isLoggedIn={ isLoggedIn } />}
            />
            <button
              onClick={ this.clearLocalStorage }>
              clear storage
            </button>
            <p> Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec efficitur pulvinar nunc at sodales. Donec eleifend diam quam, nec commodo ex mollis in. Suspendisse sollicitudin bibendum arcu vel egestas. Sed quam diam, tincidunt ut suscipit quis, fermentum sed nibh. Cras quis lacinia orci. Quisque nec mollis tortor. Sed nec porta nisi. Vestibulum mattis nisl quis nisl laoreet, id egestas erat blandit. Aliquam non eros malesuada, eleifend ante non, ornare libero. Maecenas hendrerit felis mi, tempus vulputate risus facilisis volutpat. Phasellus ipsum sem, egestas a urna ac, hendrerit pulvinar dolor. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Sed lobortis gravida finibus. Nunc porta faucibus nunc semper mattis. </p>
            <Footer />
          </Router>
        </div>
      );
    }
}

Main.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(Main);
