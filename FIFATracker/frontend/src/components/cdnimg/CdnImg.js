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

class CdnImage extends React.Component {
  constructor() {
    super();
    this.state = {
      title: null,
    };

    this.onError = this.onError.bind(this);
    this.onMouseOver = this.onMouseOver.bind(this);
  }

  onMouseOver(e) {
    const { title } = this.state;
    if (title !== null) {
      return
    };

    // TODO Load Title
    this.setState({
      title: "xD",
    })
  }

  onError(e) {
    const { default_val } = this.props;
    const src = `https://fifatracker.net/static/img/assets/${default_val}`;
    console.log(e);
    e.target.src = src;
    this.setState({
      title: "Not Found",
    })
  }

  render() {
    const { _class, fifa, imgtype, val} = this.props;
    const { title } = this.state;

    let src = null
    if (!fifa) {
      src = `https://fifatracker.net/static/img/assets/common/${imgtype}/${val}.png`;
    } else {
      src = `https://fifatracker.net/static/img/assets/${fifa}/${imgtype}/${val}.png`;
    }

    return (
      <img
        src={src}
        data-src={src}
        title={title}
        onError={this.onError}
        onMouseOver={this.onMouseOver}
        className={_class}
      />
    )
  }
}

CdnImage.propTypes = {
  _class: PropTypes.object,
  fifa: PropTypes.number,
  imgtype: PropTypes.string.isRequired,
  val: PropTypes.string.isRequired,
  default_val: PropTypes.string.isRequired,
};

export default compose(
  withLocalize
)(CdnImage);