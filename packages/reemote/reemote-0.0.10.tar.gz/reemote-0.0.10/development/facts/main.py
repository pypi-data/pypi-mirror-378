from nicegui import ui, native, app
from gui.gui import Gui
from reemote.execute import execute
from reemote.produce_grid import produce_grid
from reemote.produce_json import produce_json
from reemote.operations.server.shell import Shell


class Gui1:
    def __init__(self):
        app.storage.user["stdout"] = ""

    @ui.refreshable
    def stdout(self):
        return ui.code(app.storage.user["stdout"],language="bash").classes('w-full')

async def Perform_adhoc_command(gui, gui1):
    responses = await execute(app.storage.user["inventory"],
                              Shell(cmd=app.storage.user["command"], su=app.storage.user["su"], sudo=app.storage.user["sudo"]))
    app.storage.user["stdout"] = responses[0].cp.stdout
    gui1.stdout.refresh()
    app.storage.user["columnDefs"],app.storage.user["rowData"] = produce_grid(produce_json(responses))
    gui.execution_report.refresh()

async def get_fact(gui, gui1):
    from reemote.facts import Get_OS
    responses = await execute(app.storage.user["inventory"],Get_OS())
    app.storage.user["stdout"] = responses[0].cp.stdout
    gui1.stdout.refresh()
    app.storage.user["columnDefs"],app.storage.user["rowData"] = produce_grid(produce_json(responses))
    gui.execution_report.refresh()

async def get_arch(gui1):
    from reemote.facts import Get_Arch
    responses = await execute(app.storage.user["inventory"],Get_Arch())
    app.storage.user["stdout"] = responses[0].cp.stdout
    gui1.stdout.refresh()
    # app.storage.user["columnDefs"],app.storage.user["rowData"] = produce_grid(produce_json(responses))
    # gui.execution_report.refresh()

async def get_date(gui1):
    from reemote.facts import Get_Date
    responses = await execute(app.storage.user["inventory"],Get_Date())
    app.storage.user["stdout"] = responses[0].cp.stdout
    gui1.stdout.refresh()


@ui.page('/')
def page():
    gui = Gui()
    gui1 = Gui1()
    gui.upload_inventory()
    with ui.row():
        ui.switch('sudo',value=False).bind_value(app.storage.user, 'sudo')
        ui.switch('su',value=False).bind_value(app.storage.user, 'su')
        ui.input(label='Adhoc command').bind_value(app.storage.user, 'command')
    ui.button('Run', on_click=lambda: Perform_adhoc_command(gui, gui1))
    ui.button('Get OS', on_click=lambda: get_fact(gui, gui1))
    ui.button('Get Arch', on_click=lambda: get_arch(gui1))
    ui.button('Get Date', on_click=lambda: get_date(gui1))
    gui1.stdout()
    gui.execution_report()

# def _main_ac():
ui.run(title="Ad Hoc Controller", reload=False, port=native.find_open_port(),
       storage_secret='private key to secure the browser session cookie')
