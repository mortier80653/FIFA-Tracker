import React from 'react';
import PropTypes from 'prop-types';
import {
  Redirect,
} from "react-router-dom";
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';

import {
  Grid,
  CircularProgress,
  LinearProgress,
  FormControl,
  InputLabel,
  Select
} from '@material-ui/core';
import axiosInstance from '../../utils/axiosInstance.js';
import Dropzone from 'react-dropzone';
import api_endpoints from '../../utils/endpoints.js';
import CareerSlot from '../mycareers/CareerSlot.js';


const styles = {
  root: {
    paddingTop: '55px',
  },
  drop_container: {
    height: "100%",
    cursor: "pointer",
    fontSize: "0.8em",
    "& a": {
      color: 'var(--link)!important',
      cursor: "pointer",
    },
  },
  title: {
    color: 'var(--primaryText)!important',
    textAlign: "center",
    paddingTop: "35px",
    paddingBottom: "35px"
  },
  uploading_title: {
    color: 'var(--primaryText)!important',
    textAlign: "center",
    paddingTop: "15px",
    paddingBottom: "15px"
  },
  progressbar_root: {
    marginTop: "15px",
    marginLeft: "auto",
    marginRight: "auto",
    width: "80%",
    paddingTop: "15px",
    backgroundColor: 'var(--primaryBg)!important',
  },
  progressbar_bar: {
    backgroundColor: 'var(--progressBar)!important',
  },
  career_slot_container: {
    height: "110px",
    width: "100%",
    borderRadius: "10px",
    boxShadow: "1px 1px 10px var(--primaryBoxShadow)",
    textAlign: "center",
    backgroundColor: 'var(--secondaryBg)!important',
    '&:hover': {
      backgroundColor: 'var(--primaryShadowBg)!important',
    },
    '@media screen and (min-width: 220px) and (max-width: 599px)': {
      height: "260px",
    }
  },
  my_careers_container: {
    margin: "auto",
  },
  progress_get_careers: {
    margin: "16px",
  },
  pt15: {
    paddingTop: "15px",
  },
  fifa_select_root: {
    color: "var(--primaryText)!important",
    backgroundColor: "rgba(0, 0, 0, 0.0)",
    "& option": {
      color: "var(--primaryText)!important",
      backgroundColor: "var(--secondaryBg)!important",
    },
  },
  fifa_select_icon: {
    color: "var(--primaryText)!important",
    backgroundColor: "rgba(0, 0, 0, 0.0)",
  },
  fifa_select_select: {
    "&:before": {
      borderColor: "var(--primaryText)!important",
    },
    "&:after": {
      borderColor: "var(--primaryText)!important",
    },
  },
}

class MyDropzone extends React.Component {
  constructor() {
    super();

    this.state = {
      picked_fifa: null,
      slot: null
    };

    this.onChangeFIFA = this.onChangeFIFA.bind(this);
  }

  componentDidMount() {
    const { ft_slot, picked_fifa } = this.props
    this.setState({
      slot: ft_slot,
      picked_fifa: 19
    })
  }

  onChangeFIFA(e) {
    this.setState({
      picked_fifa: e.target.value
    })
  }

  render() {
    const { slot, picked_fifa } = this.state;
    const { handleFileUpload, classes } = this.props;

    const fifa_input_id = `fifa-input-${slot}`;

    return (
      <React.Fragment>
        <Grid
          container
          spacing={0}
          justify="center"
          alignItems="center"
          className={classes.drop_container}
        >
          <Grid item xs={4}>
            <FormControl>
              <InputLabel
                shrink
                htmlFor={fifa_input_id}
                classes={{
                  root: classes.fifa_select_root,
                }}
              >
                FIFA
              </InputLabel>
              <Select
                native
                value={picked_fifa || 19}
                onChange={this.onChangeFIFA}
                inputProps={{
                  name: 'FIFA',
                  id: fifa_input_id,
                }}
                className={classes.fifa_select_select}
                classes={{
                  root: classes.fifa_select_root,
                  icon: classes.fifa_select_icon,
                }}
              >
                <option value={19}>FIFA 19</option>
                <option value={18}>FIFA 18</option>
                <option value={17}>FIFA 17</option>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={8}>
            <Dropzone
              onDrop={ (a,r,e) => {handleFileUpload(a,r,e, slot, picked_fifa)} }
              multiple={false}
              minSize={6500000}
              maxSize={15000000}
            >
              {({getRootProps, getInputProps}) => (
                <div>
                  <div {...getRootProps({className: 'dropzone'})}>
                    <input {...getInputProps()} />
                    <p>Drag 'n' drop your file here, or <a>click</a> to select file</p>
                    <em>(You can find your game save in "Documents" -> "FIFA XX" -> "settings" -> "CareerX")</em>
                  </div>
                </div>
              )}
            </Dropzone>
          </Grid>
        </Grid>
      </ React.Fragment>

    )
  }
}

class MyCareers extends React.Component {
  constructor() {
    super();
    this.state = {
      new_career_upload_progress: [],
      check_saves_interval: null,
      careers: null,
      error: null,
    };

    this.handleFileUpload = this.handleFileUpload.bind(this);
    this.getSavesReq = this.getSavesReq.bind(this);
    this.getUploadComp = this.getUploadComp.bind(this);
  }

  getUploadComp(idx, val) {
    console.log("getUploadComp")
    const { classes } = this.props
    return (
      <Grid item lg={6} xs={12} key={idx}>
        <div className={classes.career_slot_container}>
          <span>
            <p className={classes.uploading_title}>
              <Translate id="uploading">Uploading</Translate>: {val}%
            </p>
          </span>
          <span>
            <LinearProgress
              classes={{
                root: classes.progressbar_root,
                bar: classes.progressbar_bar
              }}
              variant="determinate" value={ val }
            />
            <br></br>
            <span className={classes.pt15}>
            </span>
          </span>
        </div>
      </Grid>
    )
  }

  handleFileUpload(files, rejectedFiles, DropEvent, idx, fifa, is_update) {
//    const jwt_token = get_token();
//    if (!jwt_token) {
//      const { handleLogout } = this.props.handleLogout();
//      handleLogout();
//      return
//    }

    if (!files || files.length <= 0) {
      return
    }

    const { check_saves_interval } = this.state;
    let chck_intrval = check_saves_interval;
    if (check_saves_interval === null) {
      chck_intrval = setInterval(this.getSavesReq, 3000);
    }

    const file = files[0]
    const file_size = file.size

    // save validation as in CareerSaveFileModel
//    if (file_size < 6500000) {
//      alert("This file is not allowed. " + file_size + " bytes is too small")
//      return
//    } else if (file_size > 15000000) {
//      alert("This file is not allowed. " + file_size + " bytes is too large")
//      return
//    }

    let form_data = new FormData();
    form_data.append('uploadedfile', files[0], 'CareerFile');
    form_data.append('ft_slot', parseInt(idx, 10));
    form_data.append('fifa_edition', parseInt(fifa, 10));
    form_data.append('is_update', (is_update || false));
    axiosInstance(api_endpoints.upload_cm_save, {
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      data: form_data,
      onUploadProgress: (p) => {
        let { new_career_upload_progress, careers } = this.state
        const { classes } = this.props;
        new_career_upload_progress[idx] = Number(((p.loaded * 100) / p.total).toFixed())
        careers = this.getUploadComp(idx, new_career_upload_progress[idx])
        this.setState({
          careers: careers,
          new_career_upload_progress: new_career_upload_progress
        })
      }
    })
    .then(res => {
      let { new_career_upload_progress } = this.state
      delete new_career_upload_progress[idx]
      this.setState({
        careers: null,
        error: null,
        new_career_upload_progress: new_career_upload_progress,
        check_saves_interval: chck_intrval
      })
    });
  }

  async getSavesReq(is_first_req) {
    if (localStorage.getItem('token') === null) {
      return
    }
    const { check_saves_interval } = this.state;
    let chck_intrval = check_saves_interval;

    const { classes } = this.props;
    axiosInstance(api_endpoints.get_cm_saves, {
      method: 'GET',
      headers: {
        Authorization: `JWT ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
    })
    .then(res =>{
      if (res.status === 200) {
        return res
      } else {
        throw res
      }
    })
    .then(res => {
      const { new_career_upload_progress } = this.state
      let tmp_array = [];
      let idx = 0;

      for (let x of res.data.saves) {
        ++idx;
        if (new_career_upload_progress[idx]) {
          tmp_array.push(
            this.getUploadComp(idx, new_career_upload_progress[idx])
          )
        } else if (!Object.keys(x).length) {
          tmp_array.push(
            <Grid container item lg={6} xs={12} key={idx}>
              <div className={classes.career_slot_container}>
                <MyDropzone handleFileUpload={this.handleFileUpload} ft_slot={idx} classes={this.props.classes} />
              </div>
            </Grid>
          )
        } else {
          tmp_array.push(
            <Grid item lg={6} xs={12} key={idx}>
              <div className={classes.career_slot_container}>
                <CareerSlot
                  slot_id={idx}
                  data={x}
                  upload_handler={this.handleFileUpload}
                  handleLogout={this.props.handleLogout}
                />
              </div>
            </Grid>
          );
        }
      };

      if (res.data.in_progress.length === 0) {
        clearInterval(chck_intrval);
        chck_intrval = null;
      } else if (check_saves_interval === null) {
        chck_intrval = setInterval(this.getSavesReq, 3000);
      }

      // Prevent setting check_saves_interval to null if interval is not cleared
      if (is_first_req) {
        this.setState({
          error: null,
          careers: tmp_array,
        });
      } else {
        this.setState({
          error: null,
          careers: tmp_array,
          check_saves_interval: chck_intrval
        });
      }
    })
    .catch((error) => {
      let error_msg = "Not logged in";

      if (!error.response) {
        error_msg = "Network error. Please check your internet connection."
      }
      clearInterval(chck_intrval);
      chck_intrval = null;
      this.setState({
        error: error_msg,
        check_saves_interval: chck_intrval
      });
      if (error.response) {
        window.location.reload();
      }
    });
  }

  componentDidMount() {
    this.getSavesReq(true)
//    // Update data every 5s
//    let itrlv = setInterval(this.getSavesReq, 3000);
//    this.setState({
//      check_saves_interval: itrlv
//    });
  }

  render() {
    const { classes, isLoggedIn } = this.props;
    if (!isLoggedIn) {
      return <Redirect to="/" />
    }
    const {
      careers,
      new_career_upload_progress,
      error
    } = this.state;

    let loading = null;
    if (error !== null) {
      loading = error
    } else if (careers === null) {
      loading = (
        <CircularProgress className={classes.progress_get_careers} />
      )
    }

    return (
      <div className={classes.root}>
        <h1 className={classes.title}>
          <Translate id="my_careers_title">Your Careers</Translate>
        </h1>
        <Grid
          container
          item md={10} xs={12}
          spacing={2}
          justify="center"
          alignItems="center"
          className={classes.my_careers_container}
        >
          { careers }
          { loading }
        </Grid>
      </div>
    )
  }
}

MyCareers.propTypes = {
  classes: PropTypes.object.isRequired,
  handleLogout: PropTypes.func.isRequired,
  isLoggedIn: PropTypes.bool.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(MyCareers);