import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import {Motion, spring} from 'react-motion';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import {
  Grid,
  Hidden,
  List,
  ListItem,
  ListItemText,
  Icon,
  Tabs,
  Tab,
  Table,
  TableHead,
  TableRow,
  TableBody
} from '@material-ui/core';

import home_bg_img from '../../assets/img/background/home.jpg';

const styles ={
  root: {
    width: '100%',
    minHeight: '800px',
    paddingTop: '55px',
    backgroundImage: `url(${home_bg_img})`,
    backgroundSize: "cover",
  },

  title: {
    color: "rgba(255, 255, 255, 0.8)!important",
    textShadow: "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000",
    textAlign: "center",
    paddingTop: "95px"
  },
  subtitle: {
    color: "rgba(255, 255, 255, 0.8)!important",
    textShadow: "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000",
    textAlign: "center",
    paddingTop: "15px"
  },
  info_main: {
    color: "rgba(255, 255, 255, 0.8)!important",
    textShadow: "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000",
    textAlign: "center",
    paddingTop: "95px"
  },
  get_started_main: {
    marginTop: "40px",
    backgroundColor: 'var(--primaryBg)!important',
    paddingBottom: "40px",
  },
  get_started_title: {
    paddingTop: "10px",
    color: 'var(--primaryText)!important',
    textAlign: "center"
  },
  get_started_steps: {
    color: 'var(--primaryText)!important',
    paddingTop: "55px",
    ' & li': {
      color: 'var(--primaryText)!important',
      textAlign: "center",
    }
  },
  get_started_step2_explain: {
    paddingTop: "10px",
    paddingBottom: "25px",
    color: 'var(--primaryText)!important',
    textAlign: "center"
  },
  get_started_discord_title: {
    paddingBottom: "10px",
    color: 'var(--primaryText)!important',
    textAlign: "center"
  },
  get_started_subtitle: {
    paddingTop: "15px",
    color: 'var(--primaryText)!important',
    textAlign: "center"
  },
  discord_widget: {
    textAlign: "center"
  },
  trending_main: {
    color: "rgba(255, 255, 255, 0.8)!important",
    textShadow: "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000",
    paddingTop: "50px",
    paddingBottom: "50px"
  },
  trending_title: {
    textAlign: "center",
  },
  tabs_root: {
    color: "#00CC00"
  },
  tabs_indicator: {
    backgroundColor: "#00CC00"
  },
  ptop20: {
    paddingTop: "20px"
  },
  nested: {
    paddingLeft: "32px"
  },
  primaryColor: {
    color: 'var(--primaryText)!important'
  },

  flag: {
    width: "40px",
    height: "40px"
  }
};

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mainPopularTabVal: 0
    };

    this.handleMainPopularTabChange = this.handleMainPopularTabChange.bind(this);
    this.popularPlayersContainer = this.popularPlayersContainer.bind(this);
    this.popularTeamsContainer = this.popularTeamsContainer.bind(this);
  }

  handleMainPopularTabChange(e, newVal) {
    this.setState({
      mainPopularTabVal: newVal
    });
  }

  popularPlayersContainer() {
    const { classes } = this.props;

    return (
      <p>Players</p>
    )
  }

  popularTeamsContainer() {
    const { classes } = this.props;

    return (
      <div style={{ textAlign: "center"}}>
        <p>Teams</p>
      </div>
    )
  }

  render() {
    const { classes } = this.props;
    const { mainPopularTabVal } = this.state;
    const springConfig = {
      precision: 0,
      stiffness: 95,
      damping: 40
    }

    let popularActiveComp;
    switch (mainPopularTabVal) {
      case 0:
        popularActiveComp = this.popularPlayersContainer();
        break;
      case 1:
        popularActiveComp = this.popularTeamsContainer();
        break;
      default:
        break;
    }
    return (
      <div className={classes.root}>
        <h1 className={classes.title}>FIFA Tracker</h1>
        <h3 className={classes.subtitle}>
          <Translate id="website_subtitle">Your true career mode hub</Translate>
        </h3>
        <Hidden only={['xs', 'sm']}>
          <div className={classes.info_main}>
            <Grid
              container
              spacing={0}
              justify="center"
              alignItems="center"
            >
              <Grid item xs={4}>
                <div>
                  <Motion defaultStyle={{x: 0}} style={{x: spring(15000, springConfig)}}>
                   {value => <div>{value.x.toFixed()}</div>}
                  </Motion>
                  <Translate id="completed_seasons">Completed seasons</Translate>
                </div>
              </Grid>
              <Grid item xs={4}>
                <div>
                  <Motion defaultStyle={{x: 0}} style={{x: spring(25000, springConfig)}}>
                   {value => <div>{value.x.toFixed()}</div>}
                  </Motion>
                  <Translate id="trophies_won">Trophies won</Translate>
                </div>
              </Grid>
              <Grid item xs={4}>
                <div>
                  <Motion defaultStyle={{x: 0}} style={{x: spring(390000, springConfig)}}>
                   {value => <div>{value.x.toFixed()}</div>}
                  </Motion>
                  <Translate id="games_won">Games won</Translate>
                </div>
              </Grid>
            </Grid>
            <Grid
              container
              justify="space-evenly"
              alignItems="center"
              className={classes.ptop20}
            >
              <Grid item xs={2}>
                <div>
                  <Motion defaultStyle={{x: 0}} style={{x: spring(1598, springConfig)}}>
                   {value => <div>{value.x.toFixed()}</div>}
                  </Motion>
                  <Translate id="registered_accounts">Registered accounts</Translate>
                </div>
              </Grid>
              <Grid item xs={2}>
                <div>
                  <Motion defaultStyle={{x: 0}} style={{x: spring(3153, springConfig)}}>
                   {value => <div>{value.x.toFixed()}</div>}
                  </Motion>
                  <Translate id="uploaded_cm_saves">Uploaded CM saves</Translate>
                </div>
              </Grid>
            </Grid>
          </div>
        </Hidden>
        <div className={classes.get_started_main}>
          <Grid
            container
            justify="space-evenly"
            alignItems="baseline"
            className={classes.ptop20}
          >
            <Grid item sm={12} md={8}>
              <h3 className={classes.get_started_title}>
                <Translate id="get_started_title">Get Started</Translate>
              </h3>
              <h4 className={classes.get_started_subtitle}>
                <Translate id="get_started_subtitle">Follow the steps below and enjoy FIFATracker!</Translate>
              </h4>
              <List className={classes.get_started_steps}>
                <ListItem>
                  <ListItemText
                    primary=<Translate id="get_started_step1">Register an new account or login. It's completely free!</Translate>
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary=<Translate id="get_started_step2">Upload your CM game save, or input data manually here.</Translate>
                  />
                </ListItem>
              </List>
              <h6 className={classes.get_started_step2_explain}>
                <Translate id="get_started_step2_explain">*Only PC users can upload their game saves</Translate>
              </h6>
            </Grid>
            <Grid item sm={12} md={4}>
              <h3 className={classes.get_started_discord_title}>
                <Translate id="join_discord">Join us on Discord!</Translate>
              </h3>
              <p className={classes.discord_widget}>
                <iframe src="https://discordapp.com/widget?id=513319954636865548&theme=dark" width="350" height="500" allowtransparency="true" frameborder="0">
                </iframe>
              </p>
            </Grid>
          </Grid>
        </div>
        <div className={classes.trending_main}>
          <h2 className={classes.trending_title}>
            <Icon className="fas fa-fire"/>
            <Translate id="popular">Popular</Translate>
          </h2>
          <Grid
            container
            spacing={0}
            justify="center"
            alignItems="center"
            className={classes.ptop20}
           >
            <Grid item xs={12}>
              <Tabs
                classes={{
                  root: classes.tabs_root,
                  indicator: classes.tabs_indicator
                }}
                value={mainPopularTabVal}
                onChange={this.handleMainPopularTabChange}
                centered
              >
                <Tab
                  label=<Translate id="players">Players</Translate>
                />
                <Tab
                  label=<Translate id="teams">Teams</Translate>
                />
              </Tabs>
              { popularActiveComp }
            </Grid>
           </Grid>
        </div>
      </div>
    )
  }
}

Home.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(Home);