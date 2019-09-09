import React from 'react';
import PropTypes from 'prop-types';
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
} from '@material-ui/core';


const styles = {
  footer_root: {
    position: "absolute",
    bottom: "0",
    width: "100%",
    paddingBottom: "10px",
    color: 'var(--primaryText)!important',
    backgroundColor: 'var(--primaryBg)!important',
    ' & h5': {
      color: 'var(--primaryText)!important',
      textAlign: "center",
    },
    ' & p': {
      color: 'var(--primaryText)!important',
      textAlign: "center",
    },
  },
  icon_root: {
    width: "100%",
    height: "100%",
    overflow: "hidden",
    fontSize: "1.5rem",
    userSelect: "none",
    flexShrink: "0"
  },
  primaryColor: {
    color: 'var(--primaryText)!important'
  },
  footer_list_links: {
    paddingTop: "15px",
    ' & a': {
      color: 'var(--link)!important',
    }
  },
};

class Footer extends React.Component {
  render() {
    const { classes } = this.props;

    const PlayersLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/players/" {...props} />
    ));

    const TeamsLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/teams/" {...props} />
    ));

    const ToolsCalcLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/tools/calc/" {...props} />
    ));

    const PrivacyPolicyLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/privacy_policy/" {...props} />
    ));

    const AboutLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/about/" {...props} />
    ));

    const ContactLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/contact/" {...props} />
    ));

    return (
        <footer className={classes.footer_root}>
          <Grid container item xs={12} spacing={1} alignItems="flex-start" justify="center">
            <Grid item xs={12} md={4}>
              <h5><Translate id="quick_links">Quick Links</Translate></h5>
              <List className={classes.footer_list_links}>
                <ListItem button component={PlayersLink}>
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fas fa-users"/>
                  </ListItemIcon>
                  <ListItemText
                    primary=<Translate id="players">Players</Translate>
                  />
                </ListItem>
                <ListItem button component={TeamsLink}>
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fas fa-tshirt"/>
                  </ListItemIcon>
                  <ListItemText
                    primary=<Translate id="teams">Teams</Translate>
                  />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={4}>
              <h5><Translate id="tools">Tools</Translate></h5>
              <List className={classes.footer_list_links}>
                <ListItem button component={ToolsCalcLink}>
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fas fa-calculator"/>
                  </ListItemIcon>
                  <ListItemText
                    primary=<Translate id="calculator">Calculator</Translate>
                  />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={4}>
              <h5><Translate id="other_links">Other Links</Translate></h5>
              <List className={classes.footer_list_links}>
                <ListItem button component="a" href="https://www.patreon.com/xAranaktu">
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fab fa-patreon"/>
                  </ListItemIcon>
                  <ListItemText
                    primary="Patreon"
                  />
                </ListItem>
                <ListItem button component="a" href="https://github.com/xAranaktu/FIFA-Tracker">
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fab fa-github"/>
                  </ListItemIcon>
                  <ListItemText
                    primary="GitHub"
                  />
                </ListItem>
                <ListItem button component="a" href="https://discord.gg/3gdjKsY">
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fab fa-discord"/>
                  </ListItemIcon>
                  <ListItemText
                    primary="Discord"
                  />
                </ListItem>
                <ListItem button component={PrivacyPolicyLink}>
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fas fa-info-circle"/>
                  </ListItemIcon>
                  <ListItemText
                    primary=<Translate id="privacy_policy">Privacy Policy</Translate>
                  />
                </ListItem>
                <ListItem button component={AboutLink}>
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fas fa-info-circle"/>
                  </ListItemIcon>
                  <ListItemText
                    primary=<Translate id="about">About</Translate>
                  />
                </ListItem>
                <ListItem button component={ContactLink}>
                  <ListItemIcon className={classes.primaryColor}>
                    <Icon classes={{ root: classes.icon_root }} className="fas fa-envelope"/>
                  </ListItemIcon>
                  <ListItemText
                    primary=<Translate id="contact">Contact</Translate>
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
          <Grid container item xs={12} spacing={1} alignItems="center" justify="center">
            <Grid item xs={12}>
              <p>All FIFA assets are property of EA Sports</p>
            </Grid>
          </Grid>
          <Grid container item xs={12} spacing={1} alignItems="center" justify="center">
            <Grid item xs={12}>
              <p>&copy; FIFA Tracker 2018-2019</p>
            </Grid>
          </Grid>
        </footer>
    )
  }
}

Footer.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(Footer);