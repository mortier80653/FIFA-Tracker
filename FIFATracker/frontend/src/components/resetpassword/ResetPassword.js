import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import {
  Grid,
  Icon,
  CircularProgress,
  TextField,
  Divider,
  Button
} from '@material-ui/core';
import {
  Redirect,
} from "react-router-dom";

import axios from 'axios';
import Dropzone from 'react-dropzone';
import api_endpoints from '../../utils/endpoints.js';

const styles = {
  reset_password_form: {
    marginTop: '105px',
    paddingBottom: "10px",
    paddingTop: "10px",
    borderRadius: '15px',
    textAlign: "center",
    color: 'var(--primaryText)!important',
    backgroundColor: "var(--primaryTheme) !important",
    margin: "auto",

    '& .MuiPaper-root': {
      backgroundColor: "var(--primaryTheme) !important",
    },
    '& .MuiFormLabel-root': {
      color: "var(--primaryText) !important",
    },
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: "var(--primaryText) !important",
    },
    '& .MuiInputBase-input': {
      color: "var(--primaryText) !important",
    }
  },
  result_container: {
    paddingTop: '90px',
    textAlign: "center",
    color: 'var(--primaryText)!important',
    paddingBottom: "35px"
  },
  title: {
    paddingTop: '25px !important',
    paddingBottom: '15px !important'
  },
  divider_bg:{
    backgroundColor: "var(--dividerColor) !important",
  },
  icon_success: {
    color: 'green',
  },
  icon_failed: {
    color: 'red',
    paddingBottom: "35px"
  },
  result_title: {
    paddingBottom: "15px"
  },
  top10: {
    marginTop: "10px",
  },
}

class ResetPassword extends React.Component {
  constructor() {
    super();
    this.state = {
      req_success: null,
      resp: null,
      form_data: {},
    };
    this.doResetPassword = this.doResetPassword.bind(this);
    this.handleFormDataChange = this.handleFormDataChange.bind(this);
  }

  doResetPassword(e, data) {
    e.preventDefault();

    if (data.new_password !== data.confirm_new_password) {
      alert("Your password and confirm password does not match")
      return;
    };

    const { uidb64, token } = this.props.match.params;

    axios(api_endpoints.user_confirm_password_reset, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({
        uidb64: uidb64,
        token: token,
        new_password: data.new_password
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

  handleFormDataChange(e) {
    let new_data = this.state.form_data;
    new_data[e.target.name] = e.target.value;
    this.setState({
      form_data: new_data
    });
  }

  render() {
    const { classes, isLoggedIn } = this.props;
    const { req_success, resp } = this.state;

    let result = null;
    if (isLoggedIn) {
      return <Redirect to="/" />
    }

    let content = null;
    if (req_success === null) {
      content = (
        <form id="reset_password_form" onSubmit={ e => this.doResetPassword(e, this.state.form_data)}>
          <Grid
            container
            spacing={2}
            justify="center"
            alignItems="center"
            item xs={6}
            className={classes.reset_password_form}
          >
            <Grid item xs={10}>
              <p>
                <Translate id="confirm_pass_reset_title">Fill the form to complete your password reset request.</Translate>
              </p>
            </Grid>
            <Grid item xs={10}>
              <TextField
                name="new_password"
                variant="outlined"
                required
                fullWidth
                id="rNewPassword"
                label=<Translate id="new_password">New Password</Translate>
                type="password"
                onChange={this.handleFormDataChange}
              />
            </Grid>
            <Grid item xs={10}>
              <TextField
                name="confirm_new_password"
                variant="outlined"
                required
                fullWidth
                id="rConfirmNewPassword"
                label=<Translate id="confirm_new_password">Confirm New Password</Translate>
                type="password"
                onChange={this.handleFormDataChange}
              />
            </Grid>
            <Grid item xs={10}>
              <Divider className={classes.divider_bg} />
            </Grid>
            <Grid item xs={10}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
              >
                <Translate id="reset_password">Reset Password</Translate>
              </Button>
            </Grid>
          </Grid>
        </form>
      )
    } else if (req_success === true) {
      content = (
        <div className={classes.result_container}>
          <h1 className={classes.result_title}>
            <Translate id="success">Success</Translate>
          </h1>
          <span className={classes.icon_success}>
            <Icon className="fas fa-check-circle"/>
          </span>
          <p className={classes.top10}>
            { resp }
          </p>
        </div>
      )
    } else {
      content = (
        <div className={classes.result_container}>
          <h1 className={classes.result_title}>
            <Translate id="failed">Failed</Translate>
          </h1>
          <span className={classes.icon_failed}>
            <Icon className="fas fa-times-circle"/>
          </span>
          <p className={classes.top10}>
            <Translate id="failed_reset_pass">Something went wrong with reseting your password... Refresh page and try again</Translate>
          </p>
        </div>
      )
    }

    return (
      <React.Fragment>
        { content }
      </ React.Fragment>
    )
  }
}

ResetPassword.propTypes = {
  classes: PropTypes.object.isRequired,
  isLoggedIn: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(ResetPassword);