import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import { BrowserRouter as Router, Route, Link as RouterLink } from "react-router-dom";
import logo from '../../assets/img/logo/logo.png';
import PreferencesList from '../preferenceslist/PreferencesList.js';
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
  root: {
    width: '100%',
    color: 'var(--primaryText)!important',
    backgroundColor: 'var(--primaryBg)!important'
  },
  primaryColor: {
    color: 'var(--primaryText)!important'
  },
};

class AccPopOver extends React.Component {

  render() {
    const { classes, logoutHandler, handleCloseAccPopOver} = this.props;
    const MyCareersLink = React.forwardRef((props, ref) => (
      <RouterLink innerRef={ref} to="/my-careers/" {...props} />
    ));

    return (
      <List
        className={classes.root}
      >
        <ListItem
          button
          onClick={handleCloseAccPopOver}
        >
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-wrench"/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id="control_panel">Control Panel</Translate>
          />
        </ListItem>
        <ListItem
          button
          onClick={handleCloseAccPopOver}
          component={MyCareersLink}
        >
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-file-upload"/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id="my_careers">My Careers</Translate>
          />
        </ListItem>
        <ListItem
          button
          onClick={logoutHandler}
        >
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-sign-out-alt"/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id="sign_out">Sign Out</Translate>
          />
        </ListItem>
      </List>
    )
  }
}

AccPopOver.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(AccPopOver);