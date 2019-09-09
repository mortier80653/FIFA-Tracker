import React from 'react';
import PropTypes from 'prop-types';
import compose from 'recompose/compose';
import clsx from 'clsx';
import { withLocalize, Translate } from "react-localize-redux";
import { withStyles } from '@material-ui/styles';
import {
  List,
  ListSubheader,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  ListItemSecondaryAction,
  Switch,
  Icon,
  Collapse,
  Hidden,
} from '@material-ui/core';

const styles ={
  root: {
    width: '100%',
    minWidth: 300,
    color: 'var(--primaryText)!important',
    backgroundColor: 'var(--primaryBg)!important'
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

function ListItemLink(props) {
  return <ListItem button component="a" {...props} />;
}

class PreferencesList extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      theme: localStorage.getItem('theme'),
      active_currency: localStorage.getItem('currency'),
      active_units: localStorage.getItem('units'),
      openLang: false,
      openCurrency: false,
      openUnits: false,
    };

    this.handleOpenNestedList = this.handleOpenNestedList.bind(this);
    this.handleSwitch = this.handleSwitch.bind(this);
    this.handleChangeLang = this.handleChangeLang.bind(this);
    this.handleChangeCurrency = this.handleChangeCurrency.bind(this);
    this.handleChangeUnits = this.handleChangeUnits.bind(this);
    this.toggleTheme = this.toggleTheme.bind(this);
  }

  componentDidUpdate(prevProps, prevState) {
    const hasActiveLanguageChanged = prevProps.activeLanguage !== this.props.activeLanguage;

    if (hasActiveLanguageChanged) {
      this.addTranslationsForActiveLanguage();
    }
  }

  addTranslationsForActiveLanguage(lang) {
    const {activeLanguage} = this.props;
    if (!activeLanguage) {
      return;
    }
    import(`../../translations/${activeLanguage.code}.json`)
    .then( translations => {
      this.props.addTranslationForLanguage(translations, activeLanguage.code);
    });
  }

  handleOpenNestedList(key, e) {
    this.setState({
      [key]: !this.state[key]
    });
  }

  handleChangeLang(code, e) {
    if (this.props.activeLanguage.code === code) {
      return;
    }
    localStorage.setItem('lang', code);
    this.props.setActiveLanguage(code);
  }

  handleChangeCurrency(code, e) {
    this.setState({
      active_currency: code
    });
    localStorage.setItem('currency', code)
  }

  handleChangeUnits(code, e) {
    this.setState({
      active_units: code
    });
    localStorage.setItem('units', code)
  }

  handleSwitch(name, e) {
    this.setState({
      [name]: e.target.checked,
    });
  }

  toggleTheme(e) {
    const theme = e.target.checked ? 'dark' : 'light';

    if (theme === localStorage.getItem('theme')) {
      return;
    }
    this.setState({
      theme: theme
    });
    localStorage.setItem('theme', theme);

    document.documentElement.classList.add("color-theme-in-transition");
    document.documentElement.setAttribute('data-theme', theme)
    window.setTimeout(() => {
      document.documentElement.classList.remove("color-theme-in-transition");
    }, 1000);
  }

  render() {
    const { classes, languages} = this.props;
    const {
      openLang,
      openCurrency,
      openUnits,
      active_currency,
      active_units
    } = this.state;

    const langList = []
    languages.forEach((lang, i) => {
      if (lang.code === '_') return;

      langList.push(
        <ListItem
          button
          key={i}
          className={classes.nested}
          onClick={ (e) => this.handleChangeLang(lang.code, e) }
        >
          <ListItemIcon className={classes.primaryColor}>
            <img className={classes.flag} src={ require(`../../assets/img/lang/${lang.code}.png`) } alt={lang.name} />
          </ListItemIcon>
          <ListItemText
            primary=<Translate id={ `lang_${lang.code}` } >{lang.name}</Translate>
          />
          { localStorage.getItem('lang') === lang.code  ? <Icon className="fas fa-check"/> : null }
        </ListItem>
      )
    });

    const curList = []
    const currencies = [
      {
        name: "Euro",
        code: "eur",
        icon: "euro-sign"
      },
      {
        name: "US Dollar",
        code: "usd",
        icon: "dollar-sign"
      },
      {
        name: "British Pound",
        code: "gbp",
        icon: "pound-sign"
      }
    ]
    currencies.forEach((currency, i) => {
      curList.push(
        <ListItem
          button
          key={ i }
          className={classes.nested}
          onClick={ (e) => this.handleChangeCurrency(currency.code, e) }
        >
          <ListItemIcon className={classes.primaryColor}>
            <Icon className={ `fas fa-${currency.icon}` }/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id={ `cur_${currency.code}` } >{currency.name}</Translate>
          />
          { active_currency === currency.code  ? <Icon className="fas fa-check"/> : null }
        </ListItem>
      )
    });

    const unitsList = []
    const units = [
      {
        name: "cm / kg",
        code: "msi"
      },
      {
        name: "feet inchees / lbs",
        code: "imperial"
      }
    ]
    units.forEach((unit, i) => {
      unitsList.push(
        <ListItem
          button
          key={ i }
          className={classes.nested}
          onClick={ (e) => this.handleChangeUnits(unit.code, e) }
        >
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-weight"/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id={ `unit_${unit.code}` } >{unit.name}</Translate>
          />
          { active_units === unit.code  ? <Icon className="fas fa-check"/> : null }
        </ListItem>
      )
    });

    return (
      <List
        subheader={
          <ListSubheader
            disableSticky
            className={classes.primaryColor}
          >
            <Translate id="preferences">Preferences</Translate>
          </ListSubheader>
        }
        className={classes.root}
      >
        <ListItem>
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-moon"/>
          </ListItemIcon>
          <ListItemText
            id="switch-list-label-dark-theme"
            primary=<Translate id="night_mode">Night Mode</Translate>
          />
          <ListItemSecondaryAction>
            <Switch
              edge="end"
              onChange={ this.toggleTheme }
              checked={ this.state.theme === 'dark' ? true : false }
              inputProps={{ 'aria-labelledby': 'switch-list-label-dark-theme' }}
            />
          </ListItemSecondaryAction>
        </ListItem>
        <ListItem button onClick={ (e) => this.handleOpenNestedList("openCurrency", e) }>
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-coins"/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id="currency">Currency</Translate>
          />
          { openCurrency ? <Icon className="fas fa-angle-up"/> : <Icon className="fas fa-angle-down"/> }
        </ListItem>
        <Collapse in={ openCurrency } timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            { curList }
          </List>
        </Collapse>

        <ListItem button onClick={ (e) => this.handleOpenNestedList("openUnits", e) }>
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-ruler" style={{ width: 30 }}/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id="units">Units</Translate>
          />
          { openUnits ? <Icon className="fas fa-angle-up"/> : <Icon className="fas fa-angle-down"/> }
        </ListItem>
        <Collapse in={ openUnits } timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            { unitsList }
          </List>
        </Collapse>

        <ListItem button onClick={ (e) => this.handleOpenNestedList("openLang", e) }>
          <ListItemIcon className={classes.primaryColor}>
            <Icon className="fas fa-globe"/>
          </ListItemIcon>
          <ListItemText
            primary=<Translate id="language">Language</Translate>
          />
          { openLang ? <Icon className="fas fa-angle-up"/> : <Icon className="fas fa-angle-down"/> }
        </ListItem>
        <Collapse in={ openLang } timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            { langList }
          </List>
        </Collapse>
      </List>
    )
  }
}

PreferencesList.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withStyles(styles),
  withLocalize
)(PreferencesList);