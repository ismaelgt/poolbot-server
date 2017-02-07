var PlayersTable = React.createClass({
  getInitialState: function() {
      return {players: [], percent: 0}
  },

  componentDidMount: function() {
    this.loadData();
  },

  loadData: function() {
    $.getJSON('/leaderboard/api/', function (data) {
      this.setState({
        players: data.players
      });

      var self = this;
      var nextRefresh = moment().add(data.secondsLeft, 'seconds');
      var cacheLifetime = data.cacheLifetime;
      var updateProgressBar = setInterval(function () {
          // Give server 3 more seconds to process the request
          var secondsLeft = nextRefresh.diff(moment(), 'seconds') + 3;
          if (secondsLeft == 0) {
            clearInterval(updateProgressBar);
            self.loadData();
          };
          self.setState({percent: Math.floor((secondsLeft / cacheLifetime) * 100)});
      }, 1000);
    }.bind(this));
  },

  render: function() {
    var rows = [];
    this.state.players.forEach(function(player) {
      rows.push(<PlayerRow player={player} key={player.id} />);
    });
    var progressBar = <ProgressBar percent={this.state.percent} />;

    var rowsA = rows.slice(0, 20);
    var rowsB = rows.slice(20, 40);
    var rowsC = rows.slice(40, 60);

    return (
      <div>
        {progressBar}
        <div className="col-xs-4">
          <table className="table table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Player</th>
                    <th>Elo</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {rowsA}
            </tbody>
          </table>
        </div>

        <div className="col-xs-4">
          <table className="table table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Player</th>
                    <th>Elo</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {rowsB}
            </tbody>
          </table>
        </div>

        <div className="col-xs-4">
          <table className="table table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Player</th>
                    <th>Elo</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {rowsC}
            </tbody>
          </table>
        </div>

      </div>
    );
  }
});

var PlayerRow = React.createClass({
  render: function() {
    var diffNode = '';
    if (this.props.player.diff > 0) {
      diffNode = <button type="button" className="btn btn-success">+{this.props.player.diff}</button>;
    } else if (this.props.player.diff < 0) {
      diffNode = <button type="button" className="btn btn-danger">{this.props.player.diff}</button>;
    }

    var trClass = '';
    if (this.props.player.diff > 0) {
      trClass = 'success';
    } else if (this.props.player.diff < 0) {
      trClass = 'danger';
    }

    return (
      <tr className={trClass}>
          <th scope="row">{this.props.player.position}</th>
          <td>{this.props.player.name}</td>
          <td>{this.props.player.season_elo}</td>
          <td>{diffNode}</td>
      </tr>
    );
  }
});

var ProgressBar = React.createClass({

  render: function() {
    var style = {width: this.props.percent.toString() + '%'}
    return (
      <div className="progress">
        <div
            className="progress-bar progress-bar-striped active"
            role="progressbar"
            aria-valuenow="100"
            aria-valuemin="0"
            aria-valuemax="100"
            style={style}>
        </div>
      </div>
    )
  },
})
