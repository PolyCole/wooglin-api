import datetime
import re

import dateutil.parser
import pytz
from rest_framework import serializers

from restapi.models.sober_bro_shifts import SoberBroShift


class SoberBroShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoberBroShift
        fields = '__all__'

    def create(self, validated_data):
        """
        Creates a shift based on the information passed in.
        """

        new_shift = SoberBroShift.objects.create(
            date=validated_data['date'],
            title=validated_data['title'] if 'title' in validated_data else self.default_shift_title(validated_data),
            time_start=validated_data['time_start'],
            time_end=validated_data['time_end'],
            capacity=validated_data['capacity']
        )

        return new_shift

    def default_shift_title(self, data):
        """
        Returns the default title for a shift if it isn't already specified.
        """
        format_string = '%I:%M%p'

        "Shift on " + str(data['date'])
        title = str(data['date']) + \
                " shift from " + \
                str(data['time_start'].strftime(format_string)) + \
                " to " + \
                str(data['time_end'].strftime(format_string))

        return title

    def update(self, shift, new_data):
        """
        Updates fields in the shift, updates title too to reflect changes if necesary.
        """
        for field in new_data:
            setattr(shift, field, new_data[field])

        regex = '^\d{4}\-\d{2}\-\d{2} shift from \d{2}\:\d{2}(AM|PM) to \d{2}\:\d{2}(AM|PM)$'
        if re.search(regex, shift.title):
            shift.title = "Shift on " + str(shift.date)

        shift.save()

        return shift

    def to_internal_value(self, validated_data):
        """
        Data validation.
        """

        time_fields = ['time_start', 'time_end', 'date']

        for item in validated_data:
            if item in time_fields:
                validated_data = self.check_date_format(validated_data, item)

        today = datetime.datetime.now()
        timezone = pytz.timezone("America/Denver")
        today = timezone.localize(today)

        # Start or end time in the past.
        if validated_data['time_start'] < today or validated_data['time_end'] < today:
            raise serializers.ValidationError(
                {
                    "timeframe": "Your start or end time for the shift are in the past. Shifts in the past can only "
                                 "be altered by the administrator. "
                }
            )

        # Shift date in the past.
        if validated_data['date'] < today.date():
            raise serializers.ValidationError(
                {
                    "date": "The date you've specified is in the past. Shifts in the past can only be created by an "
                            "administrator. "
                }
            )

        # Negative capacity.
        if 'capacity' in validated_data:
            if validated_data['capacity'] <= 0:
                raise serializers.ValidationError(
                    {
                        "capacity": "Capacity must be a positive integer."
                    }
                )

        same_day_shifts = SoberBroShift.objects.filter(date=validated_data['date'])

        # Ensuring there's only one shift during any given timeslot. Overlapping is not preferable.
        if same_day_shifts.count() != 0:
            new_shift_start = validated_data['time_start']
            new_shift_end = validated_data['time_end']

            for shift in same_day_shifts:
                old_shift_start = shift.time_start
                old_shift_end = shift.time_end

                if old_shift_start < new_shift_start < old_shift_end:
                    raise serializers.ValidationError(
                        {
                            "start_conflict": "The start time of the proposed shift conflicts with an existing shift: " + str(
                                shift)
                        }
                    )

                if old_shift_start < new_shift_end < old_shift_end:
                    raise serializers.ValidationError(
                        {
                            "end_conflict": "The end time of the proposed shift conflicts with an existing shift: " + str(
                                shift)
                        }
                    )

        return super(SoberBroShiftSerializer, self).to_internal_value(validated_data)

    # Ensures we have a datetime format that plays nicely with the database.
    def check_date_format(self, data, field):
        if type(data[field]) is str:
            temp = dateutil.parser.parse(data[field])

            if temp.tzinfo is None or temp.tzinfo.utcoffset(temp) is None:
                timezone = pytz.timezone("America/Denver")
                temp = timezone.localize(temp)

            if field == 'date':
                temp = temp.date()

            data[field] = temp
        return data
