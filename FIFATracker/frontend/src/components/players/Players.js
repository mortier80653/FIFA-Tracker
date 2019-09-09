import React from 'react';
import compose from 'recompose/compose';
import { withLocalize, Translate } from "react-localize-redux";

class Players extends React.Component {
    render() {
        return (
            <h1>
              <Translate id="players">Players</Translate>b
            </h1>
        )
    }
}

export default compose(
  // withStyles(styles),
  withLocalize
)(Players);