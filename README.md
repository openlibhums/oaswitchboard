# OA Switchboard Plugin
This is a plugin for Janeway that enables OA Switchboard p1-pio messages to be sent.

## Install
1. Clone this repository into the Janeway plugins folder.
2. From the `src` directory run `python3 manage.py install_plugins oas`.
3. Run the Janeway command  for running required migrations: `python3 manage.py migrate`
4. Restart your server (Apache, Passenger, etc)
5. You can then edit add your credentials and enable the plugin at <journal>/plugins/oa-switchboard/manager/.
