import React from 'react';
import { LocalizeProvider } from "react-localize-redux";
import Main from '../main/Main.js';


class App extends React.Component {
//    constructor(props) {
//        super(props);
//    }

    componentDidMount() {
      // Theme
      const theme = localStorage.getItem('theme');
      if (theme == null || theme === 'light') {
        return;
      }
      document.documentElement.setAttribute('data-theme', theme);
    }

    render() {
        return (
          <LocalizeProvider>
            <Main />
          </LocalizeProvider>
        );
    }
}

export default App;