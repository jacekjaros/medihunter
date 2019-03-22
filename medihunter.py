import json
import time
from datetime import datetime
from pushover import Client

import click

from medicover_session import MedicoverSession, load_available_search_params


now = datetime.now()
now_formatted = now.strftime('%Y-%m-%dT02:00:00.000Z')


@click.command()
@click.option('--user', prompt=True)
@click.password_option(confirmation_prompt=False)
@click.option('--region', '-r', default=204)
@click.option('--specialization', '-s', default=16234)
@click.option('--clinic', '-c', default=-1)
@click.option('--doctor', '-o', default=-1)
@click.option('--start-date', '-d', default=now_formatted)
@click.option('--interval', '-i', default=0)
@click.option('--pushover_token', default="")
@click.option('--pushover_user', default="")
@click.option('--pushover_device', default=None)
def find_appointment(user, password, region, specialization, clinic, doctor, start_date, interval, pushover_token, pushover_user,pushover_device):
    counter = 0
    med_session = MedicoverSession(username=user, password=password)

    if (pushover_user != "") and (pushover_token != ""):
        try :
            client = Client(user_key=pushover_user, api_token=pushover_token)
            pushover_notification = True
        except Exception:
            click.secho('Pushover not initialized correctly', fg='red')
            return
    else :
        pushover_notification = False

    try :
        r = med_session.log_in()
    except Exception:
        click.secho('Unsuccessful logging in', fg='red')
        return

    click.echo('Logged in')

    med_session.load_search_form()  # TODO: can I get rid of it?

    while interval > 0 or counter < 1:
        appointments = med_session.search_appointments(
            region=region, specialization=specialization, clinic=clinic, doctor=doctor, start_date=start_date)

        if not appointments:
            click.echo(click.style(
                f'(iteration: {counter}) No results found', fg='yellow'))
        else:
            applen = len(appointments)
            notification = ""
            click.echo(click.style(f'(iteration: {counter}) Found {applen} appointments', fg='green', blink=True))
            for appointment in appointments:
                click.echo(
                    appointment.appointment_datetime + ' ' +
                    click.style(appointment.doctor_name, fg='bright_green') + ' ' +
                    appointment.clinic_name
                )
                if pushover_notification : notification = notification + appointment.appointment_datetime + ' ' + appointment.doctor_name + ' ' + appointment.clinic_name + '\n'
            if pushover_notification : client.send_message(notification, title="Found " + str(applen) + " appointments", device=pushover_device)
        counter += 1
        time.sleep(interval*60)


FIELD_NAMES = ['specialization', 'region', 'clinic', 'doctor']


@click.command()
@click.option('-f', '--field-name', type=click.Choice(FIELD_NAMES), default='specialization')
def show_params(field_name):
    params = load_available_search_params(field_name)
    for p in params:
        text = p['text']
        id_ = p['id']
        print(f' {text} (id={id_})')


@click.group()
def medihunter():
    pass

medihunter.add_command(show_params)
medihunter.add_command(find_appointment)


if __name__ == '__main__':
    medihunter()
