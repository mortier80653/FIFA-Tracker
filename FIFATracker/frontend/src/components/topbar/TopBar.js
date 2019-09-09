import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import { BrowserRouter as Router, Route, Link as RouterLink } from "react-router-dom";
import logo from '../../assets/img/logo/logo.png';
import PreferencesList from '../preferenceslist/PreferencesList.js';
import AccPopOver from '../accpopover/AccPopOver.js';
import Home from '../home/Home.js';
import Players from '../players/Players.js';


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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Hidden,
  Dialog,
  DialogContent,
  Tabs,
  Tab,
  TextField
} from '@material-ui/core';
import api_endpoints from '../../utils/endpoints.js';


const styles = {
  '@global': {
    ul: {
      margin: 0,
      padding: 0,
    },
    li: {
      listStyle: 'none',
    },
  },
  primaryColor: {
    color: 'var(--primaryText)!important'
  },
  appBar: {
    borderBottom: `1px solid var(--primaryTheme)`,
    backgroundColor: "var(--primaryTheme) !important",
    color: 'var(--primaryText)!important',
  },
  toolbar: {
    flexWrap: 'wrap',
    minHeight: '55px !important',
  },
  leftNav: {
    marginRight: "auto",
  },
  rightNav: {
    marginLeft: "auto",
  },
  username: {
    paddingLeft: "5px",
    fontSize: "1.0rem",
  },
  itemNav: {
    margin: "3px 9px",
    color: "var(--primaryText)",
  },
  iconNav: {
    margin: "3px 9px",
    color: "var(--primaryText)",
  },
  avatar: {
    margin: "5px 10px"
  },
  loginDialogContainer: {
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
  divider_bg:{
    backgroundColor: "var(--dividerColor) !important",
  },
  loginDialog: {
    backgroundColor: "var(--primaryTheme) !important",
    color: 'var(--primaryText)!important',
  },
  tabs_indicator: {
    backgroundColor: 'var(--tabsIndicator)!important',
  },
  register_form: {
    paddingTop: "20px"
  },
  fake_link:{
    color: 'var(--link)!important',
    cursor: 'pointer',
  },
};

class TopBar extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      preferencesEl: null,
      accPopOverEl: null,
      signupDialogIsOpen: false,
      resetPasswordDialogIsOpen: false,
      signUpTabVal: 0,
      register_data: {},
      login_data: {},
      reset_password_data: {},
    };

    this.handleOpenSignUpDialog = this.handleOpenSignUpDialog.bind(this);
    this.handleCloseSignUpDialog = this.handleCloseSignUpDialog.bind(this);
    this.handleSignUpTabChange = this.handleSignUpTabChange.bind(this);

    this.handleUserRegisterDataChange = this.handleUserRegisterDataChange.bind(this);

    this.handleUserLoginDataChange = this.handleUserLoginDataChange.bind(this);

    this.doRegister = this.doRegister.bind(this);
    this.doLogin = this.doLogin.bind(this);
    this.doLogout = this.doLogout.bind(this);
    this.doRequestPasswordReset = this.doRequestPasswordReset.bind(this);

    this.handleShowPreferences = this.handleShowPreferences.bind(this);
    this.handleClosePreferences = this.handleClosePreferences.bind(this);

    this.handleShowAccPopOver = this.handleShowAccPopOver.bind(this);
    this.handleCloseAccPopOver = this.handleCloseAccPopOver.bind(this);

    this.handleOpenResetPasswordDialog = this.handleOpenResetPasswordDialog.bind(this);
    this.handleCloseResetPasswordDialog = this.handleCloseResetPasswordDialog.bind(this);
    this.handleResetPasswordDataChange = this.handleResetPasswordDataChange.bind(this);
  }

  handleUserRegisterDataChange(e) {
    let new_data = this.state.register_data;
    new_data[e.target.name] = e.target.value;
    this.setState({
      register_data: new_data
    });
  }

  handleUserLoginDataChange(e) {
    let new_data = this.state.login_data;
    new_data[e.target.name] = e.target.value;
    this.setState({
      login_data: new_data
    });
  }

  handleResetPasswordDataChange(e) {
    let new_data = this.state.reset_password_data;
    new_data[e.target.name] = e.target.value;
    this.setState({
      reset_password_data: new_data
    });
  }

  handleOpenResetPasswordDialog(e) {
    let form = document.getElementById("reset_password_form");
    if (form) {form.reset()};
    this.setState({
      signupDialogIsOpen: false,
      resetPasswordDialogIsOpen: true,
    });
  }

  handleCloseResetPasswordDialog(e) {
    this.setState({
      signUpTabVal: 0,
      signupDialogIsOpen: false,
      resetPasswordDialogIsOpen: false,
    });
  }

  handleOpenSignUpDialog(e) {
    this.setState({
      signupDialogIsOpen: true,
      resetPasswordDialogIsOpen: false,
    });
  }

  handleCloseSignUpDialog(e) {
    this.setState({
      signUpTabVal: 0,
      signupDialogIsOpen: false,
      resetPasswordDialogIsOpen: false,
    });
  }

  handleSignUpTabChange(e, newVal) {
    let form = document.getElementById("login_form");
    if (form) {form.reset()};
    form = document.getElementById("register_form");
    if (form) {form.reset()};

    this.setState({
      signUpTabVal: newVal
    });
  }

  doRegister(e, data) {
    this.props.handleRegister(e, data);
    this.setState({
      signupDialogIsOpen: false,
      resetPasswordDialogIsOpen: false,
      signUpTabVal: 0,
    });
  }
  doLogin(e, data) {
    this.props.handleLogin(e, data);
    this.setState({
      signupDialogIsOpen: false,
      resetPasswordDialogIsOpen: false,
      signUpTabVal: 0,
    });
  }
  doLogout(e) {
    this.props.handleLogout(e);
    this.setState({
      accPopOverEl: null
    });
  }

  doRequestPasswordReset(e, data) {
    e.preventDefault();

    if (!data.username && !data.email) {
      alert("Username or email is required");
      return
    }

    axios(api_endpoints.user_request_password_reset, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({
        username: data.username,
        email: data.email,
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
      alert(json.msg)
      this.setState({
        resetPasswordDialogIsOpen: false
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
      })
    });
  }

  handleShowPreferences(e) {
    this.setState({
      preferencesEl: e.currentTarget
    });
  }
  handleClosePreferences(e) {
    this.setState({
      preferencesEl: null
    });
  }

  handleShowAccPopOver(e) {
    this.setState({
      accPopOverEl: e.currentTarget
    });
  }
  handleCloseAccPopOver(e) {
    this.setState({
      accPopOverEl: null
    });
  }

  passwordResetContainer() {
    const { classes } = this.props;

    return (
      <form id="reset_password_form" onSubmit={ e => this.doRequestPasswordReset(e, this.state.reset_password_data)} className={classes.reset_password_form}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <p>
              <Translate id="request_pass_reset_title">
                If you've forgotten your password you can enter your e-mail or username and we'll send out instructions on how to reset it.
              </Translate>
            </p>
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="username"
              variant="outlined"
              fullWidth
              id="rpUsername"
              label=<Translate id="username">Username</Translate>
              onChange={this.handleResetPasswordDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="email"
              variant="outlined"
              fullWidth
              id="rpEmail"
              label="Email"
              type="email"
              onChange={this.handleResetPasswordDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <Divider className={classes.divider_bg} />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
            >
              <Translate id="request_reset_password">Request Reset Password</Translate>
            </Button>
          </Grid>
        </Grid>
      </form>
    )
  }

  signupLoginContainer() {
    const { classes } = this.props;

    return (
      <form id="login_form" onSubmit={ e => this.doLogin(e, this.state.login_data)} className={classes.register_form}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              name="username"
              variant="outlined"
              required
              fullWidth
              id="lUsername"
              label=<Translate id="username">Username</Translate>
              onChange={this.handleUserLoginDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="password"
              variant="outlined"
              required
              fullWidth
              id="lPassword"
              label=<Translate id="password">Password</Translate>
              type="password"
              onChange={this.handleUserLoginDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <Divider className={classes.divider_bg} />
          </Grid>
          <Grid item xs={12}>
            <p onClick={this.handleOpenResetPasswordDialog} className={classes.fake_link}>
              Forgot your password?
            </p>
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
            >
              <Translate id="login">Login</Translate>
            </Button>
          </Grid>
        </Grid>
      </form>
    )
  }

  signupRegisterContainer() {
    const { classes } = this.props;
    return (
      <form id="register_form" onSubmit={ e => this.doRegister(e, this.state.register_data)} className={classes.register_form}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              name="username"
              variant="outlined"
              required
              fullWidth
              id="rUsername"
              label=<Translate id="username">Username</Translate>
              onChange={this.handleUserRegisterDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="email"
              variant="outlined"
              required
              fullWidth
              id="rEmail"
              label="Email"
              type="email"
              onChange={this.handleUserRegisterDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="password"
              variant="outlined"
              required
              fullWidth
              id="rPassword"
              label=<Translate id="password">Password</Translate>
              type="password"
              onChange={this.handleUserRegisterDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="confirm_password"
              variant="outlined"
              required
              fullWidth
              id="rConfirmPassword"
              label=<Translate id="confirm_password">Confirm Password</Translate>
              type="password"
              onChange={this.handleUserRegisterDataChange}
            />
          </Grid>
          <Grid item xs={12}>
            <Divider className={classes.divider_bg} />
          </Grid>
          <Grid item xs={12}>
            By registering, you agree to the <Link onClick={this.handleCloseSignUpDialog} component={RouterLink} to="/privacy_policy/">privacy policy</Link> and <Link onClick={this.handleCloseSignUpDialog} component={RouterLink} to="/terms_of_service/">terms of service</Link>.
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
            >
              <Translate id="create_account">Create New Account</Translate>
            </Button>
          </Grid>
        </Grid>
      </form>
    )
  }

  render() {
    const { classes, isLoggedIn, user } = this.props;
    const { preferencesEl, accPopOverEl, signUpTabVal } = this.state;
    const openPref = Boolean(preferencesEl);
    const openAcc = Boolean(accPopOverEl);

    const HomeLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/" {...props} />
    ));
    const PlayersLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/players/" {...props} />
    ));

    let userMenu;
    let signIn;
    if (isLoggedIn) {
      userMenu = (
        <IconButton
            className={classes.primaryColor}
            onClick={this.handleShowAccPopOver}
        >
          <Icon className="fas fa-user"/>
          <Hidden only={['xs', 'sm']}>
            <span className={classes.username}>{ user.username }</span>
          </Hidden>
        </IconButton>
      )
    } else {
      userMenu = (
        <div>
          <Hidden only={['xs', 'sm']}>
            <Button onClick={this.handleOpenSignUpDialog} href="#" size="large" color="primary" variant="contained">
              <Translate id="login">Login</Translate>
            </Button>
          </Hidden>
          <Hidden only={['md', 'lg', 'xl']}>
            <IconButton
                className={classes.primaryColor}
                onClick={this.handleOpenSignUpDialog}
            >
              <Icon className="fas fa-sign-in-alt"/>
            </IconButton>
          </Hidden>
        </div>
      )
    }

    const navLinks = (
      <React.Fragment>
        <Grid item>
          <Button className={classes.primaryColor} component={PlayersLink}>
            <Translate id="players">Players</Translate>
          </Button>
        </Grid>
        <Grid item>
          <Button className={classes.primaryColor} component={PlayersLink}>
            <Translate id="teams">Teams</Translate>
          </Button>
        </Grid>
      </React.Fragment>
    )

    let signUpActiveComp;
    switch (signUpTabVal) {
      case 0:
        signUpActiveComp = this.signupLoginContainer();
        break;
      case 1:
        signUpActiveComp = this.signupRegisterContainer();
        break;
      default:
        break;
    }

    return (
      <div>
        <AppBar position="fixed" className={classes.appBar} >
          <Toolbar className={classes.toolbar}>
            <Grid container item xs={6} spacing={0} alignItems="center" justify="flex-start">
              <Grid item>
                <Hidden xsDown>
                  <Button component={HomeLink}>
                    <img src={logo} alt="FIFATracker Logo" />
                  </Button>
                </Hidden>
                <Hidden smUp>
                  <Link className={classes.primaryColor} component={RouterLink} to="/">FIFATracker</Link>
                </Hidden>
              </Grid>
              <Hidden only={['xs', 'sm']}>
                { navLinks }
              </Hidden>
            </Grid>
            <Grid container item xs={6} spacing={1} alignItems="center" justify="flex-end">
              <Grid item>
                <Tooltip title=
                  <Translate id="preferences">Preferences</Translate>
                >
                  <IconButton
                      className={classes.primaryColor}
                      onClick={this.handleShowPreferences}
                  >
                    <Icon className="fas fa-cog"/>
                  </IconButton>
                </Tooltip>
              </Grid>
              <Grid item>
                { userMenu }
              </Grid>
            </Grid>
            <Hidden only={['md', 'lg', 'xl']}>
              <Grid container item xs={12} spacing={4} alignItems="center" justify="space-evenly">
                { navLinks }
              </Grid>
            </Hidden>
          </Toolbar>
        </AppBar>
        <Popover
          elevation={0}
          anchorEl={preferencesEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center'
          }}
          onClose={this.handleClosePreferences}
          open={openPref}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center'
          }}
        >
          <PreferencesList />
        </Popover>
        <Popover
          elevation={0}
          anchorEl={accPopOverEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center'
          }}
          onClose={this.handleCloseAccPopOver}
          open={openAcc}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center'
          }}
        >
          <AccPopOver
            logoutHandler={this.doLogout}
            handleCloseAccPopOver={this.handleCloseAccPopOver}
          />
        </Popover>
        <Dialog
          onClose={this.handleCloseResetPasswordDialog}
          aria-labelledby="reset-password-dialog"
          open={this.state.resetPasswordDialogIsOpen}
          className={classes.loginDialogContainer}
        >
          <DialogContent className={classes.loginDialog}>
            <Grid
              container
              spacing={0}
              justify="center"
              alignItems="center"
            >
              <Grid item xs={12}>
                {this.passwordResetContainer()}
              </Grid>
            </Grid>
          </DialogContent>
        </Dialog>
        <Dialog
          onClose={this.handleCloseSignUpDialog}
          aria-labelledby="signup-dialog"
          open={this.state.signupDialogIsOpen}
          className={classes.loginDialogContainer}
        >
          <DialogContent className={classes.loginDialog}>
            <Grid
              container
              spacing={0}
              justify="center"
              alignItems="center"
            >
              <Grid item xs={12}>
                <Tabs
                  classes={{
                    indicator: classes.tabs_indicator
                  }}
                  value={signUpTabVal}
                  onChange={this.handleSignUpTabChange}
                  centered
                >
                  <Tab
                    label=<Translate id="login">Login</Translate>
                  />
                  <Tab
                    label=<Translate id="register">Register</Translate>
                  />
                </Tabs>
                { signUpActiveComp }
              </Grid>
            </Grid>
          </DialogContent>
        </Dialog>
      </div>

    )
  }
}

TopBar.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(TopBar);