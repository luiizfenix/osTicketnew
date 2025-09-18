<?php
if (!defined('OSTSCPINC') || !$thisstaff
        || !$thisstaff->hasPerm(Ticket::PERM_CREATE, false))
        die('Access Denied');

$info=array();
$info=Format::htmlchars(($errors && $_POST)?$_POST:$info, true);

if ($_SESSION[':form-data'] && !$_GET['tid'])
  unset($_SESSION[':form-data']);

//  Use thread entry to seed the ticket
if (!$user && $_GET['tid'] && ($entry = ThreadEntry::lookup($_GET['tid']))) {
    if ($entry->getThread()->getObjectType() == 'T')
      $oldTicketId = $entry->getThread()->getObjectId();
    if ($entry->getThread()->getObjectType() == 'A')
      $oldTaskId = $entry->getThread()->getObjectId();

    $_SESSION[':form-data']['message'] = Format::htmlchars($entry->getBody());
    $_SESSION[':form-data']['ticketId'] = $oldTicketId;
    $_SESSION[':form-data']['taskId'] = $oldTaskId;
    $_SESSION[':form-data']['eid'] = $entry->getId();
    $_SESSION[':form-data']['timestamp'] = $entry->getCreateDate();

    if ($entry->user_id)
       $user = User::lookup($entry->user_id);

     if (($m= TicketForm::getInstance()->getField('message'))) {
         $k = 'attach:'.$m->getId();
         unset($_SESSION[':form-data'][$k]);
        foreach ($entry->getAttachments() as $a) {
          if (!$a->inline && $a->file) {
            $_SESSION[':form-data'][$k][$a->file->getId()] = $a->getFilename();
            $_SESSION[':uploadedFiles'][$a->file->getId()] = $a->getFilename();
          }
        }
     }
}

if (!$info['topicId'])
    $info['topicId'] = $cfg->getDefaultTopicId();

$forms = array();
if ($info['topicId'] && ($topic=Topic::lookup($info['topicId']))) {
    foreach ($topic->getForms() as $F) {
        if (!$F->hasAnyVisibleFields())
            continue;
        if ($_POST) {
            $F = $F->instanciate();
            $F->isValidForClient();
        }
        $forms[] = $F;
    }
}

if ($_POST)
    $info['duedate'] = Format::date(strtotime($info['duedate']), false, false, 'UTC');
?>
<form action="tickets.php?a=open" method="post" class="save"  enctype="multipart/form-data">
 <?php csrf_token(); ?>
 <input type="hidden" name="do" value="create">
 <input type="hidden" name="a" value="open">
<div style="margin-bottom:20px; padding-top:5px;">
    <div class="pull-left flush-left">
        <h2><?php echo __('Open a New Ticket');?></h2>
    </div>
</div>
 <div class="form-container">
    <div class="form-row">
        <div class="form-col-full">
            <em><strong><?php echo __('User and Collaborators'); ?></strong>: </em>
            <div class="error"><?php echo $errors['user']; ?></div>
        </div>
    </div>
    <?php
    if ($user) { ?>
        <div class="form-row">
            <div class="form-col-label"><?php echo __('User'); ?>:</div>
            <div class="form-col-field">
                <div id="user-info">
                    <input type="hidden" name="uid" id="uid" value="<?php echo $user->getId(); ?>" />
                    <?php if ($thisstaff->hasPerm(User::PERM_EDIT)) { ?>
                    <a href="#" onclick="javascript:
                    $.userLookup('ajax.php/users/<?php echo $user->getId(); ?>/edit',
                    function (user) {
                        $('#user-name').text(user.name);
                        $('#user-email').text(user.email);
                    });
                    return false;
                    ">
                    <?php } else { ?>
                    <a href="#">
                    <?php } ?>
                    <i class="icon-user"></i>
                    <span id="user-name"><?php echo Format::htmlchars($user->getName()); ?></span>
                    &lt;<span id="user-email"><?php echo $user->getEmail(); ?></span>&gt;
                    </a>
                    <a class="inline button" style="overflow:inherit" href="#"
                    onclick="javascript:
                    $.userLookup('ajax.php/users/select/'+$('input#uid').val(),
                    function(user) {
                        $('input#uid').val(user.id);
                        $('#user-name').text(user.name);
                        $('#user-email').text('<'+user.email+'>');
                    });
                    return false;
                    "><i class="icon-retweet"></i> <?php echo __('Change'); ?></a>
                </div>
            </div>
        </div>
        <?php
    } else { //Fallback: Just ask for email and name
        ?>
        <div class="form-row" id="userRow">
            <div class="form-col-label"><?php echo __('User'); ?>:</div>
            <div class="form-col-field">
                <span>
                <select class="userSelection" name="name" id="user-name"
                data-placeholder="<?php echo __('Select User'); ?>">
                </select>
                </span>
                <a class="inline button" style="overflow:inherit" href="#"
                onclick="javascript:
                $.userLookup('ajax.php/users/lookup/form', function (user) {
                    var newUser = new Option(user.email + ' - ' + user.name, user.id, true, true);
                    return $(&quot;#user-name&quot;).append(newUser).trigger('change');
                });
                return false;
                "><i class="icon-plus"></i> <?php echo __('Add New'); ?></a>
                <span class="error">*</span>
                <br/><span class="error"><?php echo $errors['name']; ?></span>
            </div>
            <div>
            <input type="hidden" size=45 name="email" id="user-email" class="attached"
            placeholder="<?php echo __('User Email'); ?>"
            autocomplete="off" autocorrect="off" value="<?php echo $info['email']; ?>" />
            </div>
        </div>
        <?php
    } ?>
    <div class="form-row" id="ccRow">
        <div class="form-col-label"><?php echo __('Cc'); ?>:</div>
        <div class="form-col-field">
            <span>
            <select class="collabSelections" name="ccs[]" id="cc_users_open" multiple="multiple"
            ref="tags" data-placeholder="<?php echo __('Select Contacts'); ?>">
            </select>
            </span>
            <a class="inline button" style="overflow:inherit" href="#"
            onclick="javascript:
            $.userLookup('ajax.php/users/lookup/form', function (user) {
                var newUser = new Option(user.name, user.id, true, true);
                return $(&quot;#cc_users_open&quot;).append(newUser).trigger('change');
            });
            return false;
            "><i class="icon-plus"></i> <?php echo __('Add New'); ?></a>
            <br/><span class="error"><?php echo $errors['ccs']; ?></span>
        </div>
    </div>
    <?php
    if ($cfg->notifyONNewStaffTicket()) {
        ?>
    <div class="form-row no_border">
        <div class="form-col-label">
        <?php echo __('Ticket Notice');?>:
        </div>
        <div class="form-col-field">
        <select id="reply-to" name="reply-to">
            <option value="all"><?php echo __('Alert All'); ?></option>
            <option value="user"><?php echo __('Alert to User'); ?></option>
            <option value="none">&mdash; <?php echo __('Do Not Send Alert'); ?> &mdash;</option>
        </select>
        </div>
    </div>
    <?php } ?>
    <div class="form-row">
        <div class="form-col-full">
            <em><strong><?php echo __('Ticket Information and Options');?></strong>:</em>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-label required">
            <?php echo __('Ticket Source');?>:
        </div>
        <div class="form-col-field">
            <select name="source">
                <?php
                $source = $info['source'] ?: 'Phone';
                $sources = Ticket::getSources();
                unset($sources['Web'], $sources['API']);
                foreach ($sources as $k => $v)
                    echo sprintf('<option value="%s" %s>%s</option>',
                            $k,
                            ($source == $k ) ? 'selected="selected"' : '',
                            $v);
                ?>
            </select>
            &nbsp;<font class="error"><b>*</b>&nbsp;<?php echo $errors['source']; ?></font>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-label required">
            <?php echo __('Help Topic'); ?>:
        </div>
        <div class="form-col-field">
            <select name="topicId" onchange="javascript:
                    var data = $(':input[name]', '#dynamic-form').serialize();
                    $.ajax(
                        'ajax.php/form/help-topic/' + this.value,
                        {
                        data: data,
                        dataType: 'json',
                        success: function(json) {
                            $('#dynamic-form').empty().append(json.html);
                            $(document.head).append(json.media);
                        }
                        });">
                <?php
                if ($topics=$thisstaff->getTopicNames(false, false)) {
                    if (count($topics) == 1)
                        $selected = 'selected="selected"';
                    else { ?>
                    <option value="" selected >&mdash; <?php echo __('Select Help Topic'); ?> &mdash;</option>
<?php                   }
                    foreach($topics as $id =>$name) {
                        echo sprintf('<option value="%d" %s %s>%s</option>',
                            $id, ($info['topicId']==$id)?'selected="selected"':'',
                            $selected, $name);
                    }
                    if (count($topics) == 1 && !$forms) {
                        if (($T = Topic::lookup($id)))
                            $forms =  $T->getForms();
                    }
                }
                ?>
            </select>
            &nbsp;<font class="error"><b>*</b>&nbsp;<?php echo $errors['topicId']; ?></font>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-label">
            <?php echo __('Department'); ?>:
        </div>
        <div class="form-col-field">
            <select name="deptId">
                <option value="" selected >&mdash; <?php echo __('Select Department'); ?>&mdash;</option>
                <?php
                if($depts=$thisstaff->getDepartmentNames(true)) {
                    foreach($depts as $id =>$name) {
                        if (!($role = $thisstaff->getRole($id))
                            || !$role->hasPerm(Ticket::PERM_CREATE)
                        ) {
                            // No access to create tickets in this dept
                            continue;
                        }
                        echo sprintf('<option value="%d" %s>%s</option>',
                                $id, ($info['deptId']==$id)?'selected="selected"':'',$name);
                    }
                }
                ?>
            </select>
            &nbsp;<font class="error"><?php echo $errors['deptId']; ?></font>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-label">
            <?php echo __('SLA Plan');?>:
        </div>
        <div class="form-col-field">
            <select name="slaId">
                <option value="0" selected="selected" >&mdash; <?php echo __('System Default');?> &mdash;</option>
                <?php
                if($slas=SLA::getSLAs()) {
                    foreach($slas as $id =>$name) {
                        echo sprintf('<option value="%d" %s>%s</option>',
                                $id, ($info['slaId']==$id)?'selected="selected"':'',$name);
                    }
                }
                ?>
            </select>
            &nbsp;<font class="error">&nbsp;<?php echo $errors['slaId']; ?></font>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-label">
            <?php echo __('Due Date');?>:
        </div>
        <div class="form-col-field">
            <?php
            $duedateField = Ticket::duedateField('duedate', $info['duedate']);
            $duedateField->render();
            ?>
            &nbsp;<font class="error">&nbsp;<?php echo $errors['duedate']; ?> &nbsp; <?php echo $errors['time']; ?></font>
            <em><?php echo __('Time is based on your time
                    zone');?>&nbsp;(<?php echo $cfg->getTimezone($thisstaff); ?>)</em>
        </div>
    </div>
    <?php
    if($thisstaff->hasPerm(Ticket::PERM_ASSIGN, false)) { ?>
    <div class="form-row">
        <div class="form-col-label"><?php echo __('Assign To');?>:</div>
        <div class="form-col-field">
            <select id="assignId" name="assignId">
                <option value="0" selected="selected">&mdash; <?php echo __('Select an Agent OR a Team');?> &mdash;</option>
                <?php
                $users = Staff::getStaffMembers(array(
                            'available' => true,
                            'staff' => $thisstaff,
                            ));
                if ($users) {
                    echo '<OPTGROUP label="'.sprintf(__('Agents (%d)'), count($users)).'">';
                    foreach ($users as $id => $name) {
                        $k="s$id";
                        echo sprintf('<option value="%s" %s>%s</option>',
                                    $k, (($info['assignId']==$k) ? 'selected="selected"' : ''), $name);
                    }
                    echo '</OPTGROUP>';
                }

                if(($teams=Team::getActiveTeams())) {
                    echo '<OPTGROUP label="'.sprintf(__('Teams (%d)'), count($teams)).'">';
                    foreach($teams as $id => $name) {
                        $k="t$id";
                        echo sprintf('<option value="%s" %s>%s</option>',
                                    $k,(($info['assignId']==$k)?'selected="selected"':''),$name);
                    }
                    echo '</OPTGROUP>';
                }
                ?>
            </select>&nbsp;<span class='error'>&nbsp;<?php echo $errors['assignId']; ?></span>
        </div>
    </div>
    <?php } ?>
    <div id="dynamic-form">
    <?php
        $options = array('mode' => 'create');
        foreach ($forms as $form) {
            print $form->getForm($_SESSION[':form-data'])->getMedia();
            include(STAFFINC_DIR .  'templates/dynamic-form.tmpl.php');
        }
    ?>
    </div>
    <?php
    //is the user allowed to post replies??
    if ($thisstaff->getRole()->hasPerm(Ticket::PERM_REPLY)) { ?>
    <div class="form-row">
        <div class="form-col-full">
            <em><strong><?php echo __('Response');?></strong>: <?php echo __('Optional response to the above issue.');?></em>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-full">
        <?php
        if($cfg->isCannedResponseEnabled() && ($cannedResponses=Canned::getCannedResponses())) {
            ?>
            <div style="margin-top:0.3em;margin-bottom:0.5em">
                <?php echo __('Canned Response');?>:&nbsp;
                <select id="cannedResp" name="cannedResp">
                    <option value="0" selected="selected">&mdash; <?php echo __('Select a canned response');?> &mdash;</option>
                    <?php
                    foreach($cannedResponses as $id =>$title) {
                        echo sprintf('<option value="%d">%s</option>',$id,$title);
                    }
                    ?>
                </select>
                &nbsp;&nbsp;
                <label class="checkbox inline"><input type='checkbox' value='1' name="append" id="append" checked="checked"><?php echo __('Append');?></label>
            </div>
        <?php
        }
            $signature = '';
            if ($thisstaff->getDefaultSignatureType() == 'mine')
                $signature = $thisstaff->getSignature(); ?>
            <textarea
                class="<?php if ($cfg->isRichTextEnabled()) echo 'richtext';
                    ?> draft draft-delete" data-signature="<?php
                    echo Format::viewableImages(Format::htmlchars($signature, true)); ?>"
                data-signature-field="signature" data-dept-field="deptId"
                placeholder="<?php echo __('Initial response for the ticket'); ?>"
                name="response" id="response" cols="21" rows="8"
                style="width:80%;" <?php
list($draft, $attrs) = Draft::getDraftAndDataAttrs('ticket.staff.response', false, $info['response']);
echo $attrs; ?>><?php echo ThreadEntryBody::clean($_POST ? $info['response'] : $draft);
            ?></textarea>
                <div class="attachments">
<?php
print $response_form->getField('attachments')->render();
?>
                </div>
            <div class="form-row">
                <div class="form-col-label"><?php echo __('Ticket Status');?>:</div>
                <div class="form-col-field">
                    <select name="statusId">
                    <?php
                    $statusId = $info['statusId'] ?: $cfg->getDefaultTicketStatusId();
                    $states = array('open');
                    if ($thisstaff->hasPerm(Ticket::PERM_CLOSE, false))
                        $states = array_merge($states, array('closed'));
                    foreach (TicketStatusList::getStatuses(
                                array('states' => $states)) as $s) {
                        if (!$s->isEnabled()) continue;
                        $selected = ($statusId == $s->getId());
                        echo sprintf('<option value="%d" %s>%s</option>',
                                $s->getId(),
                                $selected
                                 ? 'selected="selected"' : '',
                                __($s->getName()));
                    }
                    ?>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-col-label"><?php echo __('Signature');?>:</div>
                <div class="form-col-field">
                    <?php
                    $info['signature']=$info['signature']?$info['signature']:$thisstaff->getDefaultSignatureType();
                    ?>
                    <label><input type="radio" name="signature" value="none" checked="checked"> <?php echo __('None');?></label>
                    <?php
                    if($thisstaff->getSignature()) { ?>
                        <label><input type="radio" name="signature" value="mine"
                            <?php echo ($info['signature']=='mine')?'checked="checked"':''; ?>> <?php echo __('My Signature');?></label>
                    <?php
                    } ?>
                    <label><input type="radio" name="signature" value="dept"
                        <?php echo ($info['signature']=='dept')?'checked="checked"':''; ?>> <?php echo sprintf(__('Department Signature (%s)'), __('if set')); ?></label>
                </div>
            </div>
        </div>
    </div>
    <?php
    } //end canPostReply
    ?>
    <div class="form-row">
        <div class="form-col-full">
            <em><strong><?php echo __('Internal Note');?></strong>
            <font class="error">&nbsp;<?php echo $errors['note']; ?></font></em>
        </div>
    </div>
    <div class="form-row">
        <div class="form-col-full">
            <textarea
                class="<?php if ($cfg->isRichTextEnabled()) echo 'richtext';
                    ?> draft draft-delete"
                placeholder="<?php echo __('Optional internal note (recommended on assignment)'); ?>"
                name="note" cols="21" rows="6" style="width:80%;" <?php
list($draft, $attrs) = Draft::getDraftAndDataAttrs('ticket.staff.note', false, $info['note']);
echo $attrs; ?>><?php echo ThreadEntryBody::clean($_POST ? $info['note'] : $draft);
            ?></textarea>
        </div>
    </div>
</div>
<p style="text-align:center;">
    <input type="submit" name="submit" value="<?php echo _P('action-button', 'Open');?>">
    <input type="reset"  name="reset"  value="<?php echo __('Reset');?>">
    <input type="button" name="cancel" value="<?php echo __('Cancel');?>" onclick="javascript:
        $(this.form).find('textarea.richtext')
          .redactor('plugin.draft.deleteDraft');
        window.location.href='tickets.php'; " />
</p>
</form>
<script type="text/javascript">
$(function() {
    $('input#user-email').typeahead({
        source: function (typeahead, query) {
            $.ajax({
                url: "ajax.php/users?q="+query,
                dataType: 'json',
                success: function (data) {
                    typeahead.process(data);
                }
            });
        },
        onselect: function (obj) {
            $('#uid').val(obj.id);
            $('#user-name').val(obj.name);
            $('#user-email').val(obj.email);
        },
        property: "/bin/true"
    });

   <?php
    // Popup user lookup on the initial page load (not post) if we don't have a
    // user selected
    if (!$_POST && !$user) {?>
    setTimeout(function() {
      $.userLookup('ajax.php/users/lookup/form', function (user) {
        window.location.href = window.location.href+'&uid='+user.id;
      });
    }, 100);
    <?php
    } ?>
});

$(function() {
    $('a#editorg').click( function(e) {
        e.preventDefault();
        $('div#org-profile').hide();
        $('div#org-form').fadeIn();
        return false;
     });

    $(document).on('click', 'form.org input.cancel', function (e) {
        e.preventDefault();
        $('div#org-form').hide();
        $('div#org-profile').fadeIn();
        return false;
    });

    $('.userSelection').select2({
      width: '450px',
      minimumInputLength: 3,
      ajax: {
        url: "ajax.php/users/local",
        dataType: 'json',
        data: function (params) {
          return {
            q: params.term,
          };
        },
        processResults: function (data) {
          return {
            results: $.map(data, function (item) {
              return {
                text: item.email + ' - ' + item.name,
                slug: item.slug,
                email: item.email,
                id: item.id
              }
            })
          };
          $('#user-email').val(item.name);
        }
      }
    });

    $('.userSelection').on('select2:select', function (e) {
      var data = e.params.data;
      $('#user-email').val(data.email);
    });

    $('.userSelection').on("change", function (e) {
      var data = $('.userSelection').select2('data');
      var data = data[0].text;
      var email = data.substr(0,data.indexOf(' '));
      $('#user-email').val(data.substr(0,data.indexOf(' ')));
     });

    $('.collabSelections').select2({
      width: '450px',
      minimumInputLength: 3,
      ajax: {
        url: "ajax.php/users/local",
        dataType: 'json',
        data: function (params) {
          return {
            q: params.term,
          };
        },
        processResults: function (data) {
          return {
            results: $.map(data, function (item) {
              return {
                text: item.name,
                slug: item.slug,
                id: item.id
              }
            })
          };
        }
      }
    });

  });
</script>
