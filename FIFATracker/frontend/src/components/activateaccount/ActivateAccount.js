import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import {
  Grid,
  Icon,
  CircularProgress
} from '@material-ui/core';
import {
  Redirect,
} from "react-router-dom";

import axios from 'axios';
import Dropzone from 'react-dropzone';
import api_endpoints from '../../utils/endpoints.js';

const styles = {
  root: {
    paddingTop: '90px',
    textAlign: "center",
    color: 'var(--primaryText)!important',
  },
  icon_success: {
    color: 'green',
  },
  icon_failed: {
    color: 'red',
    paddingBottom: "35px"
  },
  result_container: {
    paddingBottom: "35px"
  },
  title: {
    paddingBottom: "15px"
  },
  progress: {
    margin: "16px",
  },
  top10: {
    marginTop: "10px",
  },
}

class ActivateAccount extends React.Component {
  constructor() {
    super();
    this.state = {
      req_success: null,
      resp: null,
    };
  }

  componentDidMount() {
    const { isLoggedIn } = this.props;
    if (isLoggedIn) {
      return
    }

    const { uidb64, token } = this.props.match.params;

    axios(api_endpoints.user_activate, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({
        uidb64: uidb64,
        token: token
      })
    })
    .then(res => {
        if (res.ok) {
          return res.json();
        } else {
          throw res;
        }
      }
    )
    .then((json) => {
      this.setState({
        resp: json.msg,
        req_success: true,
      });
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
        this.setState({
          req_success: false,
        });
      })
    });
  }

  render() {
    const { classes, isLoggedIn } = this.props;
    const { req_success } = this.state;

    let result = null;
    if (isLoggedIn) {
      return <Redirect to="/" />
    }

    if (req_success === null) {
      result = (
        <CircularProgress className={classes.progress} />
      )
    } else if (req_success === true) {
      result = (
        <div className={classes.result_container}>
          <h1 className={classes.title}>
            <Translate id="success">Success</Translate>
          </h1>
          <span className={classes.icon_success}>
            <Icon className="fas fa-check-circle"/>
          </span>
          <p className={classes.top10}>
            <Translate id="success_activate_msg">Your account has been activated, you can login now.</Translate>
          </p>
        </div>
      )
    } else {
      result = (
        <div className={classes.result_container}>
          <h1 className={classes.title}>
            <Translate id="failed">Failed</Translate>
          </h1>
          <span className={classes.icon_failed}>
            <Icon className="fas fa-times-circle"/>
          </span>
          <p className={classes.top10}>
            <Translate id="failed_activate_msg">Something went wrong with activating your account....</Translate>
          </p>
        </div>
      )
    }

    return (
      <div className={classes.root}>
        { result }
      </div>
    )
  }
}

ActivateAccount.propTypes = {
  classes: PropTypes.object.isRequired,
  isLoggedIn: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(ActivateAccount);