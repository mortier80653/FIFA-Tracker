import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import {
  Grid,
  Button,
  CircularProgress,
  Icon
} from '@material-ui/core';
import axios from 'axios';
import Dropzone from 'react-dropzone';
import api_endpoints from '../../utils/endpoints.js';

import CdnImg from '../cdnimg/CdnImg.js';

const styles = {
  root: {
  },
  container: {
    position: "relative",
    height: "110px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    '@media screen and (min-width: 220px) and (max-width: 599px)': {
      height: "250px",
    }
  },
  title: {
    position: "absolute",
    textAlign: "left",
    top: "5px",
    left: "95px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    width: "50%",
  },
  club_record: {
    position: "absolute",
    textAlign: "left",
    top: "57px",
    left: "95px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    width: "50%",
  },
  season_container: {
    position: "absolute",
    textAlign: "left",
    top: "45px",
    left: "95px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    width: "50%",
  },
  slot_id: {
    position: "absolute",
    top: "5px",
    left: "5px",
  },
  badge: {
    position: "absolute",
    top: "10px",
    left: "40px",
    zIndex: "1",
    '& img': {
      width: "45px",
      height: "45px",
    }
  },
  head: {
    position: "absolute",
    top: "25px",
    left: "10px",
    zIndex: "2",
    '& img': {
      width: "75px",
      height: "75px",
    }
  },
  progress: {
    margin: "16px",
  },
  submit: {
    margin: "6px",
  },
  file_status_container: {
    position: "absolute",
    top: "10px",
    right: "170px",
    '@media screen and (min-width: 220px) and (max-width: 599px)': {
      bottom: "65px",
      top: "auto!important",
      right: "0",
      left: "0",
    }
  },
  team_rating_container: {
    display: "inline-grid",
    position: "absolute",
    top: "10px",
    right: "160px",
    '@media screen and (min-width: 220px) and (max-width: 599px)': {
      bottom: "65px",
      top: "auto!important",
      right: "0",
      left: "0",
    }
  },
  stars_container: {
    padding: "5px",
    marginBottom: "10px",
    display: "inline-flex",
    backgroundColor: 'rgba(8, 8, 8, 0.7)',
    borderRadius: "5px",
  },
  rat_desc_container: {
    wordSpacing: "10px"
  },
  rat_container: {
    wordSpacing: "20px"
  },
  actions_container: {
    position: "absolute",
    display: "inline-grid",
    top: "10px",
    right: "20px",
    width: "125px",
    '@media screen and (min-width: 220px) and (max-width: 599px)': {
      top: "auto!important",
      bottom: "10px",
      left: "10px",
      display: "inline-flex",
      width: "95%",
    }
  },
  icon_success: {
    color: 'green',
    fontSize: "2.5rem",
  },
  icon_failed: {
    color: 'red',
    fontSize: "2.5rem",
  },
  star: {
    color: 'yellow',
    width: "20%",
    height: "100%",
    fontSize: "1.1rem",
    padding: "1px",
  },
  smallerfont: {
    fontSize: "0.8rem",
  }
}



class CareerSlot extends React.Component {
  constructor() {
    super();

    this.onDelete = this.onDelete.bind(this);
    this.onUpdate = this.onUpdate.bind(this);
    this.doUpdate = this.doUpdate.bind(this);
  }

  onUpdate(e) {
    console.log("onUpdate")
    this.refs.fileUploader.click();
  }

  onDelete(e) {

    let params = {}
    if (this.props.data.id) {
      params = {
        to_delete: "cs_model",
        model_id: this.props.data.id
      }
    } else {
      params = {
        to_delete: "slot",
        slot_id: this.props.slot_id
      }
    }
    console.log(this.props.data)
    axios(api_endpoints.delete_cm_save, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: params,
    })
    .then(res => {
      window.location.reload();
    });
  }

  doUpdate(e) {
    const { upload_handler, slot_id, data} = this.props
    console.log("doUpdate")
    const is_update = true;

    upload_handler(e.target.files, [], {}, slot_id, 0, is_update)
  }

  render() {
    const { classes, slot_id, data } = this.props;
    let file_status = null;
    let status_msg = null;
    let is_in_progress = true;
    let del_btn = null;
    switch (data.file_process_status_code) {
      case -1:
        // in Queue
        let position_in_queue = data.position_in_queue + 1;
        let approx_wait_time = <Translate id="unknown">Unknown</Translate>
        if (position_in_queue < 1) {
          position_in_queue = <Translate id="unknown">Unknown</Translate>;
        } else {
          approx_wait_time = `${(position_in_queue * 2)} min.`
        }
        status_msg = (
          <p className={classes.smallerfont}>
            <Translate id="file_in_queue">In Queue</Translate>: {position_in_queue}
            <br></br>
            <em>(<Translate id="approx_wait_time">Approx. wait time</Translate>: {approx_wait_time})</em>
          </p>
        )
        file_status = (
          <React.Fragment>
            <CircularProgress className={classes.progress} />
          </React.Fragment>
        )
        break;
      case 0:
        // File is being processed
        status_msg = (
          <p className={classes.smallerfont}>
            Status: {data.file_process_status_msg}
            <br></br>
            <em>(<Translate id="approx_wait_time_in_progress">Approx. wait time: Below 2 min</Translate>)</em>
          </p>
        )
        file_status = (
          <React.Fragment>
            <CircularProgress className={classes.progress} />
          </React.Fragment>
        )
        break;
      case 1:
        status_msg = (
          <p className={classes.smallerfont}>
            Error: {data.file_process_status_msg}
            <br></br>
          </p>
        )
        file_status = (
          <React.Fragment>
            <span>
              <Icon
                classes={{
                  root: classes.icon_failed,
                }}
                className="fas fa-times-circle"
              />
            </span>
          </React.Fragment>
        )
        del_btn = (
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
            onClick={this.onDelete}
          >
            <Translate id="delete">Delete</Translate>
          </Button>
        )
        break;
      case 2:
        status_msg = (
          <p>
            Done: {data.file_process_status_msg}
          </p>
        )
        file_status = (
          <React.Fragment>
            <span>
              <Icon
                classes={{
                  root: classes.icon_success,
                }}
                className="fas fa-check-circle"
              />
            </span>
          </React.Fragment>
        )
        break;
      default:
        is_in_progress = false
        break;
    }

    let title = data.save_original_name;
    let season = null;
    let record = null;
    let update_btn = null;
    if (!is_in_progress) {
      title = (data.firstname + " " + data.surname)
      season = (
        <span><Translate id="season">Season</Translate>: { data.season_display }</span>
      )
      let p = data.m_hist.games_played
      let w = data.m_hist.wins
      let d = data.m_hist.draws
      let l = data.m_hist.losses
      let gd = data.m_hist.goals_for - data.m_hist.goals_against
      let r = `${p}/${w}/${d}/${l}/${gd}`
      record = (
        <div className={classes.smallerfont}>
          <br></br>
          <Translate id="total_club_record">Total Club Record</Translate>:
          <br></br>
          { r } (P/W/D/L/GD)
        </div>
      )
      update_btn = (
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
          onClick={this.onUpdate}
        >
          <Translate id="update">Update</Translate>
        </Button>
      )
      del_btn = (
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
          onClick={this.onDelete}
        >
          <Translate id="delete">Delete</Translate>
        </Button>
      )
    }

    const img_val = `l${data.teamid || data.clubteamid}`;
    const head_val = `gmh${data.headid}`;

    let small_img = <CdnImg fifa={19} imgtype={"crest"} val={img_val} default_val={"common/crest/notfound.png"}/>

    let main_img = null;
    if (data.headid) {
      main_img = <CdnImg imgtype={"managerheads"} val={head_val} default_val={"common/heads/notfound.png"}/>
    } else {
      main_img = <CdnImg fifa={19} imgtype={"crest"} val={img_val} default_val={"common/crest/notfound.png"}/>
      small_img = null
    }

    let stars = null;
    let team_rating_comp = null;
    if (data.team_power) {
      const ovr = data.team_power.ovr
      stars = [];
      let idx = 0;
      let full_stars = 0;
      let half_stars = 0;
      let empty_stars = 0;
      if (ovr >= 83) {
        full_stars = 5;
        half_stars = 0;
        empty_stars = 0;
      } else if (ovr >= 79) {
        full_stars = 4;
        half_stars = 1;
        empty_stars = 0;
      } else if (ovr >= 75) {
        full_stars = 4;
        half_stars = 0;
        empty_stars = 1;
      } else if (ovr >= 71) {
        full_stars = 3;
        half_stars = 1;
        empty_stars = 1;
      } else if (ovr >= 69) {
        full_stars = 3;
        half_stars = 0;
        empty_stars = 2;
      } else if (ovr >= 67) {
        full_stars = 2;
        half_stars = 1;
        empty_stars = 2;
      } else if (ovr >= 65) {
        full_stars = 2;
        half_stars = 0;
        empty_stars = 3;
      } else if (ovr >= 63) {
        full_stars = 1;
        half_stars = 1;
        empty_stars = 3;
      } else if (ovr >= 60) {
        full_stars = 1;
        half_stars = 0;
        empty_stars = 4;
      } else {
        full_stars = 0;
        half_stars = 1;
        empty_stars = 4;
      }

      for (let x = 0; x < full_stars; x++) {
        idx++;
        stars.push(
          <Icon
            key={idx}
            classes={{
              root: classes.star,
            }}
            className="fas fa-star"
          />
        )
      }
      for (let x = 0; x < half_stars; x++) {
        idx++;
        stars.push(
          <Icon
            key={idx}
            classes={{
              root: classes.star,
            }}
            className="fas fa-star-half-alt"
          />
        )
      }
      for (let x = 0; x < empty_stars; x++) {
        idx++;
        stars.push(
          <Icon
            key={idx}
            classes={{
              root: classes.star,
            }}
            className="far fa-star"
          />
        )
      }

      team_rating_comp = (
        <React.Fragment>
          <div className={classes.team_rating_container}>
            <span title={`${data.team_power.ovr} OVR`} className={classes.stars_container}>
              { stars }
            </span>
            <span className={classes.rat_desc_container}>
              <Translate id="att">ATT</Translate> <Translate id="mid">MID</Translate> <Translate id="def">DEF</Translate>
            </span>
            <span className={classes.rat_container}>
              { data.team_power.att } { data.team_power.mid } { data.team_power.def }
            </span>
          </div>
        </React.Fragment>
      )
    }
    return (
      <div className={classes.root}>
        <Grid
          container
          spacing={0}
          justify="center"
          alignItems="center"
        >
          <Grid className={ classes.container } item xs={12}>
            <span className={classes.slot_id}>
              { slot_id }
            </span>
            <span className={classes.head}>
              { main_img }
            </span>
            <span className={classes.badge}>
              { small_img }
            </span>
            <span title="Hidden because it may contain your personal data" className={classes.title}>
              { title }
              { status_msg }
            </span>
            <span title="Played/Wins/Draws/Losses/Goals Difference" className={classes.club_record}>
              { record }
            </span>
            <div className={classes.file_status_container}>
              { file_status }
            </div>
            <span className={classes.season_container}>
              { season }
            </span>
            { team_rating_comp }
            <span className={classes.actions_container}>
              { update_btn }
              { del_btn }
            </span>
            <input type='file' id='file' ref="fileUploader" onChange={this.doUpdate} style={{display: 'none'}}/>
          </Grid>
        </Grid>
      </div>
    )
  }
}

CareerSlot.propTypes = {
  classes: PropTypes.object.isRequired,
  slot_id: PropTypes.number.isRequired,
  data: PropTypes.object.isRequired,
  handleLogout: PropTypes.func.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(CareerSlot);